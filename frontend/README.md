# Quiz Application Frontend

A modern React frontend for the TechXConf Quiz Application, built with TypeScript, Vite, and Tailwind CSS.

## Features

- **Modern React**: Built with React 18 and TypeScript for type safety
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Authentication**: Complete login/register flow with JWT tokens
- **Interactive Quizzes**: Real-time quiz taking with timer and progress tracking
- **Results & Analytics**: Detailed quiz results with question-by-question breakdown
- **Leaderboards**: User rankings by topic and overall performance
- **Profile Management**: User profile viewing and management

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **React Router DOM** - Client-side routing
- **React Hook Form** - Form handling
- **Axios** - HTTP client
- **React Hot Toast** - Toast notifications

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- Backend API running (see main README)

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment setup:**
   Create a `.env` file in the frontend directory:
   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Base UI components (Button, Input, etc.)
│   │   ├── Layout.tsx      # Main app layout with navigation
│   │   └── ProtectedRoute.tsx
│   ├── contexts/           # React contexts
│   │   └── AuthContext.tsx # Authentication context
│   ├── pages/              # Page components
│   │   ├── HomePage.tsx    # Landing page
│   │   ├── LoginPage.tsx   # Login form
│   │   ├── RegisterPage.tsx # Registration form
│   │   ├── QuizzesPage.tsx # Quiz listing
│   │   ├── QuizDetailPage.tsx # Quiz details
│   │   ├── QuizPage.tsx    # Interactive quiz taking
│   │   ├── ResultsPage.tsx # Quiz results
│   │   ├── LeaderboardPage.tsx # User rankings
│   │   └── ProfilePage.tsx # User profile
│   ├── services/           # API services
│   │   └── api.ts         # HTTP client and API methods
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts       # API response types
│   ├── utils/              # Utility functions
│   │   └── cn.ts          # Class name utilities
│   ├── App.tsx            # Main app component
│   └── main.tsx           # Entry point
├── public/                 # Static assets
├── index.html             # HTML template
├── package.json           # Dependencies and scripts
├── tailwind.config.js     # Tailwind configuration
├── tsconfig.json          # TypeScript configuration
└── vite.config.ts         # Vite configuration
```

## Key Features

### Authentication System

- JWT-based authentication with automatic token refresh
- Secure token storage in localStorage
- Protected routes with automatic redirect to login
- User profile management

### Quiz Taking Flow

1. **Browse Quizzes** - View available quizzes with filtering
2. **Quiz Details** - See quiz information before starting
3. **Take Quiz** - Interactive quiz interface with:
   - Progress tracking
   - Timer (if quiz has time limit)
   - One question at a time
   - Real-time answer validation
4. **Results** - Detailed results with:
   - Score percentage
   - Question-by-question breakdown
   - Time taken
   - Performance analytics

### Responsive Design

- Mobile-first responsive design
- Optimized for desktop, tablet, and mobile devices
- Clean, modern UI with consistent design system
- Accessible components with proper ARIA labels

## API Integration

The frontend integrates with the FastAPI backend through a comprehensive API service layer:

- **Authentication**: Login, register, logout, profile management
- **Quizzes**: List quizzes, get details, start sessions
- **Quiz Sessions**: Answer questions, track progress, submit results
- **Leaderboards**: View rankings by topic and overall
- **Results**: Detailed quiz results and analytics

## Development

### Code Organization

- **Components**: Reusable UI components with consistent props interfaces
- **Pages**: Route-specific components handling page logic
- **Services**: API integration and business logic
- **Types**: Comprehensive TypeScript definitions for all API responses
- **Utils**: Helper functions and utilities

### State Management

- **React Context**: Authentication state management
- **Local State**: Component-specific state with React hooks
- **API State**: Server state with loading and error handling

### Styling

- **Tailwind CSS**: Utility-first CSS framework
- **Custom Design System**: Consistent colors, spacing, and typography
- **Component Variants**: Flexible component styling with variant props
- **Responsive**: Mobile-first responsive design patterns

## Building for Production

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Preview the build:**
   ```bash
   npm run preview
   ```

3. **Deploy:**
   The `dist/` directory contains the production build ready for deployment to any static hosting service.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `/api/v1` |

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

1. Follow the existing code style and patterns
2. Use TypeScript for type safety
3. Write responsive, accessible components
4. Test your changes thoroughly
5. Update documentation as needed

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure the backend is running on the correct port
   - Check the `VITE_API_URL` environment variable
   - Verify CORS settings in the backend

2. **Authentication Issues**
   - Clear localStorage if tokens are corrupted
   - Check token expiration and refresh logic
   - Verify backend authentication endpoints

3. **Build Issues**
   - Clear `node_modules` and reinstall dependencies
   - Check for TypeScript errors
   - Verify all imports are correct

### Development Tips

- Use React Developer Tools for debugging
- Check browser console for errors
- Use network tab to debug API calls
- Test responsive design in device mode