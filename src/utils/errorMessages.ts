/**
 * Error messages and user-friendly instructions
 */

export interface ErrorDetails {
  title: string;
  message: string;
  action?: string;
  actionType?: 'switch-tab' | 'retry' | 'contact-support';
}

/**
 * Parse error message and return user-friendly details with actionable instructions
 */
export function parseAuthError(error: any): ErrorDetails {
  const errorMessage = error?.response?.data?.detail || error?.message || String(error);
  const errorLower = errorMessage.toLowerCase();

  // User already exists - suggest login
  if (errorLower.includes('already exists') || errorLower.includes('already registered')) {
    return {
      title: 'Аккаунт уже существует',
      message: 'Пользователь с таким email уже зарегистрирован.',
      action: 'Войти в существующий аккаунт',
      actionType: 'switch-tab'
    };
  }

  // Invalid credentials - suggest registration or password reset
  if (errorLower.includes('invalid credentials') || 
      errorLower.includes('invalid email or password') ||
      errorLower.includes('wrong password')) {
    return {
      title: 'Неверные данные',
      message: 'Email или пароль указаны неверно. Проверьте правильность введённых данных.',
      action: 'Зарегистрировать новый аккаунт',
      actionType: 'switch-tab'
    };
  }

  // User not found - suggest registration
  if (errorLower.includes('user not found') || 
      errorLower.includes('not found') ||
      errorLower.includes('does not exist')) {
    return {
      title: 'Пользователь не найден',
      message: 'Аккаунт с таким email не существует.',
      action: 'Создать новый аккаунт',
      actionType: 'switch-tab'
    };
  }

  // Email validation errors
  if (errorLower.includes('invalid email') || errorLower.includes('email is invalid')) {
    return {
      title: 'Неверный email',
      message: 'Введите корректный адрес электронной почты.',
      action: 'Попробовать снова',
      actionType: 'retry'
    };
  }

  // Password too short
  if (errorLower.includes('password') && 
      (errorLower.includes('short') || errorLower.includes('at least'))) {
    return {
      title: 'Слишком короткий пароль',
      message: 'Пароль должен содержать минимум 6 символов.',
      action: 'Попробовать снова',
      actionType: 'retry'
    };
  }

  // Username validation
  if (errorLower.includes('username') && 
      (errorLower.includes('short') || errorLower.includes('invalid'))) {
    return {
      title: 'Неверное имя пользователя',
      message: 'Имя пользователя должно содержать минимум 3 символа.',
      action: 'Попробовать снова',
      actionType: 'retry'
    };
  }

  // Rate limiting
  if (errorLower.includes('rate limit') || errorLower.includes('too many')) {
    return {
      title: 'Слишком много попыток',
      message: 'Превышен лимит запросов. Пожалуйста, подождите несколько минут.',
      action: 'Попробовать позже',
      actionType: 'retry'
    };
  }

  // Network errors
  if (errorLower.includes('network') || errorLower.includes('connection')) {
    return {
      title: 'Ошибка соединения',
      message: 'Не удалось подключиться к серверу. Проверьте интернет-соединение.',
      action: 'Попробовать снова',
      actionType: 'retry'
    };
  }

  // Server errors
  if (errorLower.includes('500') || errorLower.includes('server error')) {
    return {
      title: 'Ошибка сервера',
      message: 'Произошла ошибка на сервере. Попробуйте позже.',
      action: 'Связаться с поддержкой',
      actionType: 'contact-support'
    };
  }

  // Email confirmation required
  if (errorLower.includes('confirm') || errorLower.includes('verification')) {
    return {
      title: 'Требуется подтверждение',
      message: 'Проверьте вашу почту и подтвердите регистрацию по ссылке из письма.',
      action: 'Понятно',
      actionType: 'retry'
    };
  }

  // Default error
  return {
    title: 'Ошибка',
    message: errorMessage || 'Произошла неизвестная ошибка. Попробуйте снова.',
    action: 'Попробовать снова',
    actionType: 'retry'
  };
}

/**
 * Get user-friendly error message for display
 */
export function getErrorMessage(error: any): string {
  const details = parseAuthError(error);
  return `${details.title}: ${details.message}`;
}

/**
 * Check if error suggests switching to login
 */
export function shouldSwitchToLogin(error: any): boolean {
  const errorMessage = error?.response?.data?.detail || error?.message || String(error);
  const errorLower = errorMessage.toLowerCase();
  return errorLower.includes('already exists') || errorLower.includes('already registered');
}

/**
 * Check if error suggests switching to registration
 */
export function shouldSwitchToRegister(error: any): boolean {
  const errorMessage = error?.response?.data?.detail || error?.message || String(error);
  const errorLower = errorMessage.toLowerCase();
  return errorLower.includes('not found') || errorLower.includes('does not exist');
}











