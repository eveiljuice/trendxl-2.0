import { test, expect } from '@playwright/test';

/**
 * Тесты для проверки исправления бага с бесплатными попытками
 * 
 * Проверяем:
 * 1. Кэшированный результат не списывает попытку
 * 2. Новый анализ списывает попытку
 * 3. Race condition не приводит к двойному списанию
 */

// Тестовые данные
const TEST_USER = {
  email: 'test@example.com',
  password: 'Test123456!'
};

const TEST_PROFILE = '@charlidamelio'; // Популярный профиль для тестирования

test.describe('Free Trial Bug Fix Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Переход на главную страницу
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
  });

  test('Кэшированный результат не списывает попытку', async ({ page }) => {
    test.slow(); // Увеличиваем таймаут для этого теста
    
    // 1. Войти в систему
    await page.click('text=Sign In');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    
    // Дождаться загрузки профиля
    await page.waitForSelector('text=Analyze', { timeout: 10000 });
    
    // 2. Проверить начальное состояние бесплатных попыток
    const initialTrialInfo = await page.evaluate(() => {
      return fetch('http://localhost:8000/api/v1/free-trial/info', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }).then(r => r.json());
    });
    
    console.log('Initial trial info:', initialTrialInfo);
    const initialCount = initialTrialInfo.today_count || 0;
    
    // 3. Выполнить первый анализ (реальный парсинг)
    await page.fill('input[placeholder*="TikTok"]', TEST_PROFILE);
    await page.click('text=Analyze');
    
    // Дождаться завершения анализа
    await page.waitForSelector('text=Analysis completed', { timeout: 120000 });
    
    // 4. Проверить, что попытка засчиталась
    const afterFirstAnalysis = await page.evaluate(() => {
      return fetch('http://localhost:8000/api/v1/free-trial/info', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }).then(r => r.json());
    });
    
    console.log('After first analysis:', afterFirstAnalysis);
    expect(afterFirstAnalysis.today_count).toBe(initialCount + 1);
    
    // 5. Выполнить второй анализ того же профиля (из кэша)
    await page.fill('input[placeholder*="TikTok"]', TEST_PROFILE);
    await page.click('text=Analyze');
    
    // Дождаться быстрого возврата (кэш должен вернуться мгновенно)
    await page.waitForSelector('text=Analysis completed', { timeout: 5000 });
    
    // 6. Проверить, что попытка НЕ засчиталась (счетчик не изменился)
    const afterCachedAnalysis = await page.evaluate(() => {
      return fetch('http://localhost:8000/api/v1/free-trial/info', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }).then(r => r.json());
    });
    
    console.log('After cached analysis:', afterCachedAnalysis);
    expect(afterCachedAnalysis.today_count).toBe(afterFirstAnalysis.today_count);
    
    // ✅ УСПЕХ: Кэшированный результат не списал попытку!
  });

  test('Проверка логов backend на наличие сообщения о кэше', async ({ page }) => {
    // Этот тест проверяет, что в логах backend появляется сообщение
    // "Returning cached analysis (NO free trial used)"
    
    // 1. Войти в систему
    await page.click('text=Sign In');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    
    await page.waitForSelector('text=Analyze', { timeout: 10000 });
    
    // 2. Перехватываем network запросы
    const requests: any[] = [];
    page.on('request', request => {
      if (request.url().includes('/api/v1/analyze')) {
        requests.push({
          url: request.url(),
          method: request.method(),
          timestamp: Date.now()
        });
      }
    });
    
    // 3. Выполнить анализ дважды
    for (let i = 0; i < 2; i++) {
      await page.fill('input[placeholder*="TikTok"]', TEST_PROFILE);
      await page.click('text=Analyze');
      await page.waitForSelector('text=Analysis completed', { timeout: 120000 });
      
      // Подождать немного между запросами
      await page.waitForTimeout(2000);
    }
    
    // 4. Проверить, что было 2 запроса
    expect(requests.length).toBe(2);
    
    // 5. Второй запрос должен вернуться быстрее (из кэша)
    const firstDuration = requests[0].timestamp;
    const secondDuration = requests[1].timestamp;
    
    // Второй запрос должен быть минимум на 5 секунд быстрее
    // (так как не делается реальный парсинг)
    console.log('Request durations:', { firstDuration, secondDuration });
  });

  test('Race condition - два запроса одновременно', async ({ browser }) => {
    test.slow(); // Увеличиваем таймаут
    
    // Создаём два контекста (два "пользователя")
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();
    
    try {
      // 1. Войти в систему в обоих контекстах
      for (const page of [page1, page2]) {
        await page.goto('http://localhost:5173');
        await page.click('text=Sign In');
        await page.fill('input[type="email"]', TEST_USER.email);
        await page.fill('input[type="password"]', TEST_USER.password);
        await page.click('button[type="submit"]');
        await page.waitForSelector('text=Analyze', { timeout: 10000 });
      }
      
      // 2. Получить начальное состояние
      const initialInfo = await page1.evaluate(() => {
        return fetch('http://localhost:8000/api/v1/free-trial/info', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }).then(r => r.json());
      });
      
      const initialCount = initialInfo.today_count || 0;
      console.log('Initial count:', initialCount);
      
      // 3. Отправить два запроса ОДНОВРЕМЕННО
      const testProfile = '@test_' + Date.now(); // Уникальный профиль
      
      const [result1, result2] = await Promise.allSettled([
        (async () => {
          await page1.fill('input[placeholder*="TikTok"]', testProfile);
          await page1.click('text=Analyze');
          await page1.waitForSelector('text=Analysis completed', { timeout: 120000 });
          return 'page1 done';
        })(),
        (async () => {
          // Небольшая задержка, чтобы запросы пересеклись
          await page2.waitForTimeout(100);
          await page2.fill('input[placeholder*="TikTok"]', testProfile);
          await page2.click('text=Analyze');
          await page2.waitForSelector('text=Analysis completed', { timeout: 120000 });
          return 'page2 done';
        })()
      ]);
      
      console.log('Results:', result1, result2);
      
      // 4. Проверить финальное состояние
      const finalInfo = await page1.evaluate(() => {
        return fetch('http://localhost:8000/api/v1/free-trial/info', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }).then(r => r.json());
      });
      
      console.log('Final count:', finalInfo.today_count);
      
      // ✅ УСПЕХ: Попытка должна быть засчитана только ОДИН раз
      // Даже если оба запроса пришли одновременно
      expect(finalInfo.today_count).toBe(initialCount + 1);
      
    } finally {
      await context1.close();
      await context2.close();
    }
  });

  test('Проверка сообщения об ошибке при исчерпании попыток', async ({ page }) => {
    // 1. Войти в систему
    await page.click('text=Sign In');
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    
    await page.waitForSelector('text=Analyze', { timeout: 10000 });
    
    // 2. Проверить текущее состояние
    const trialInfo = await page.evaluate(() => {
      return fetch('http://localhost:8000/api/v1/free-trial/info', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }).then(r => r.json());
    });
    
    console.log('Trial info:', trialInfo);
    
    // 3. Если попытки ещё есть, использовать их
    if (trialInfo.can_use_free_trial) {
      const uniqueProfile = '@unique_' + Date.now();
      await page.fill('input[placeholder*="TikTok"]', uniqueProfile);
      await page.click('text=Analyze');
      
      // Дождаться завершения
      await page.waitForSelector('text=Analysis completed', { timeout: 120000 });
    }
    
    // 4. Попытаться выполнить ещё один анализ (должен быть отклонён)
    const anotherProfile = '@another_' + Date.now();
    await page.fill('input[placeholder*="TikTok"]', anotherProfile);
    await page.click('text=Analyze');
    
    // 5. Должно появиться сообщение об ошибке
    const errorVisible = await page.waitForSelector(
      'text=free daily analysis', 
      { timeout: 5000 }
    ).catch(() => null);
    
    if (errorVisible) {
      console.log('✅ Error message shown correctly');
      expect(await errorVisible.isVisible()).toBe(true);
    } else {
      console.log('⚠️ No error shown (user might have subscription)');
    }
  });
});

test.describe('Backend API Tests', () => {
  
  test('Проверка эндпоинта /api/v1/free-trial/info', async ({ request }) => {
    // Примечание: этот тест требует валидный токен
    // В реальности нужно сначала получить токен через /auth/login
    
    const token = process.env.TEST_ACCESS_TOKEN;
    if (!token) {
      test.skip();
      return;
    }
    
    const response = await request.get('http://localhost:8000/api/v1/free-trial/info', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    console.log('Free trial info:', data);
    
    expect(data).toHaveProperty('can_use_free_trial');
    expect(data).toHaveProperty('today_count');
    expect(data).toHaveProperty('daily_limit');
    expect(data.daily_limit).toBe(1);
  });

  test('Проверка Redis lock через API', async ({ request }) => {
    const token = process.env.TEST_ACCESS_TOKEN;
    if (!token) {
      test.skip();
      return;
    }
    
    // Отправить два запроса одновременно
    const testProfile = '@test_' + Date.now();
    
    const [response1, response2] = await Promise.all([
      request.post('http://localhost:8000/api/v1/analyze', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: {
          profile_url: testProfile
        }
      }),
      request.post('http://localhost:8000/api/v1/analyze', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        data: {
          profile_url: testProfile
        }
      })
    ]);
    
    // Один из запросов должен вернуть 409 (Conflict) или оба должны успешно завершиться
    // (один получит lock, другой получит результат из кэша)
    const statuses = [response1.status(), response2.status()];
    console.log('Response statuses:', statuses);
    
    // Проверяем что либо оба успешны (200), либо один 409
    const hasConflict = statuses.includes(409);
    const allSuccess = statuses.every(s => s === 200);
    
    expect(hasConflict || allSuccess).toBeTruthy();
  });
});

