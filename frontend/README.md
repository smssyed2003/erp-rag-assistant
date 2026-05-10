# ERP RAG Frontend

A modern, responsive Angular frontend for the ERP RAG (Retrieval-Augmented Generation) Assistant.

## Features

- **Modern UI/UX**: Clean, responsive design with smooth animations
- **Real-time Chat**: Interactive chat interface with typing indicators
- **Mobile-First**: Fully responsive design that works on all devices
- **Accessibility**: ARIA labels and keyboard navigation support
- **Error Handling**: User-friendly error messages with dismissible alerts
- **Production Ready**: Optimized build configuration for deployment

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm start
```

The application will be available at `http://localhost:4200`

### Build for Production

```bash
npm run build
```

The build artifacts will be stored in the `dist/erp-rag-frontend/` directory.

### Environment Configuration

Update the backend URL in the appropriate environment file:

- `src/environments/environment.ts` - Development
- `src/environments/environment.prod.ts` - Production

## Deployment

### Static Hosting

The built application can be deployed to any static hosting service:

1. Build the application: `npm run build`
2. Deploy the `dist/erp-rag-frontend/` directory to your hosting service

### Supported Platforms

- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Firebase Hosting
- Any static web server

### Environment Variables

Set the `backendUrl` in the production environment file to point to your deployed backend API.

## Architecture

- **Angular 17**: Modern Angular framework
- **TypeScript**: Type-safe development
- **RxJS**: Reactive programming for API calls
- **SCSS**: Component-scoped styling
- **Responsive Design**: Mobile-first approach

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow Angular style guide
2. Use TypeScript strictly
3. Test on multiple browsers
4. Ensure responsive design works on mobile devices