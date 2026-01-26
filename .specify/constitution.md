# Project Constitution

This document defines the foundational rules and standards for the fit-app project.

## User Experience Standards

### Consistent Navigation

All pages MUST include a consistent navigation bar 

**Navigation Implementation Rules:**
- Navigation must appear at the top of every page
- Navigation styling must be consistent across all pages
- All navigation links must be functional and properly resolve relative paths
- The navigation bar must be visible without scrolling on page load

### Visual Consistency

- All pages must use the shared stylesheet (`components/styles.css`)
- Color schemes, typography, and spacing must be consistent across pages
- Interactive elements (buttons, links, forms) must have consistent styling
- Error and success messages must use the same notification component

### Responsive Design

- All pages must be mobile-friendly
- Navigation must remain usable on smaller screens
- Forms must be accessible on touch devices

## Code Standards

### Frontend

- Use semantic HTML elements
- Include proper accessibility attributes (labels, ARIA when needed)
- JavaScript modules should be used for code organization
- API configuration must be centralized and consistent

### Backend

- All API endpoints must return consistent JSON response formats
- Error responses must include meaningful error messages
- Security headers must be applied to all responses
- Input validation must be performed on all user-provided data

### Infrastructure

- Use Infrastructure as Code (Bicep/ARM) for all Azure resources
- Follow Azure naming conventions
- Use managed identities over connection strings where possible
- Enable CORS only for known frontend origins

## Package & Dependency Policy

### Deprecated Package Handling

When encountering deprecated npm packages:
1. **DO NOT** use deprecated packages in new code
2. **DO** find actively maintained alternatives
3. **DO** document the replacement in commit messages
4. **DO** update any existing code using deprecated packages when touched

### Version Management

- Pin dependency versions in package.json
- Review and update dependencies quarterly
- Security vulnerabilities must be addressed within 7 days
