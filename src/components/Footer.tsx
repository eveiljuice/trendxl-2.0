import React from 'react';

interface FooterProps {
  className?: string;
}

const Footer: React.FC<FooterProps> = ({ className = '' }) => {
  const currentYear = new Date().getFullYear();

  // Navigation links
  const navigationLinks = [
    { name: 'Product', href: '#product' },
    { name: 'Trends', href: '#trends' },
    { name: 'For whom', href: '#forwhom' },
    { name: 'Feature', href: '#feature' },
  ];

  // Privacy policies by region
  const privacyPolicies = [
    {
      name: 'U.S. Privacy Notice',
      href: '/usprivacynotice',
      region: 'US'
    },
    {
      name: 'UAE Privacy Policy',
      href: '/uaeprivacypolicy',
      region: 'UAE'
    },
    {
      name: 'EU Privacy Policy',
      href: '/euprivacypolicy',
      region: 'EU'
    },
  ];

  // Legal documents
  const legalLinks = [
    { name: 'Terms of Use', href: '/termsofuse' },
  ];

  return (
    <footer className={`bg-white border-t border-border ${className}`}>
      <div className="container mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Top section: Navigation + CTA - адаптивные отступы */}
        <div className="mb-8 sm:mb-12">
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center space-y-6 sm:space-y-8 lg:space-y-0">
            {/* Navigation Links - адаптивные отступы */}
            <div className="flex flex-wrap gap-4 sm:gap-6 md:gap-8">
              {navigationLinks.map((link, index) => (
                <a
                  key={index}
                  href={link.href}
                  className="text-xs sm:text-sm font-medium text-muted-foreground hover:text-foreground transition-colors duration-150"
                >
                  {link.name}
                </a>
              ))}
            </div>
            
            {/* CTA Button - адаптивные размеры */}
            <div className="flex-shrink-0 w-full lg:w-auto">
              <a
                href="https://tally.so/r/wbJBQ7"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-accent inline-block w-full lg:w-auto text-center text-sm sm:text-base"
              >
                Get trends now!
              </a>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-border mb-8"></div>

        {/* Bottom section: Legal + Copyright - адаптивные отступы */}
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center space-y-4 sm:space-y-6 lg:space-y-0">
          {/* Legal Links - адаптивные отступы */}
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6">
            {/* Privacy Policies - адаптивные отступы */}
            <div className="flex flex-col space-y-1.5 sm:space-y-2">
              <span className="text-xs font-semibold text-foreground uppercase tracking-wide">
                Privacy Policies
              </span>
              <div className="flex flex-col sm:flex-row gap-2 sm:gap-4">
                {privacyPolicies.map((policy, index) => (
                  <a
                    key={index}
                    href={policy.href}
                    className="text-xs text-muted-foreground hover:text-foreground transition-colors duration-150"
                    title={`Privacy Policy for ${policy.region}`}
                  >
                    {policy.name}
                  </a>
                ))}
              </div>
            </div>

            {/* Terms of Use - адаптивные отступы */}
            <div className="flex flex-col space-y-1.5 sm:space-y-2">
              <span className="text-xs font-semibold text-foreground uppercase tracking-wide">
                Legal
              </span>
              <div className="flex flex-col sm:flex-row gap-2 sm:gap-4">
                {legalLinks.map((legal, index) => (
                  <a
                    key={index}
                    href={legal.href}
                    className="text-xs text-muted-foreground hover:text-foreground transition-colors duration-150"
                  >
                    {legal.name}
                  </a>
                ))}
              </div>
            </div>
          </div>

          {/* Copyright */}
          <div className="text-xs text-muted-foreground">
            © {currentYear} LeadGet FZ-LLC. All rights reserved
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
