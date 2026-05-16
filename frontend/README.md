# CodeLens Frontend

React + TypeScript + Vite application for the CodeLens web dashboard.

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at http://localhost:5173

### 3. Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### 4. Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/
│   └── index.html           # HTML template
├── src/
│   ├── index.tsx            # Application entry point
│   ├── App.tsx              # Main App component
│   ├── index.css            # Global styles
│   ├── components/          # React components
│   │   ├── Layout/          # Layout components
│   │   ├── Graph/           # Graph visualization (Phase 2)
│   │   ├── Documentation/   # Documentation viewer (Phase 3)
│   │   ├── QA/              # Q&A interface (Phase 4)
│   │   └── TechDebt/        # Tech debt dashboard (Phase 5)
│   ├── services/
│   │   └── api.ts           # API client
│   ├── hooks/               # Custom React hooks
│   └── types/
│       └── index.ts         # TypeScript type definitions
├── package.json
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── postcss.config.js        # PostCSS configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Flow** - Graph visualization (Phase 2)
- **Axios** - HTTP client
- **React Query** - Data fetching and caching
- **Zustand** - State management

## Development

### Adding New Components

Components are organized by feature:

```tsx
// Example: Creating a new component
import { FC } from 'react';

interface MyComponentProps {
  title: string;
}

export const MyComponent: FC<MyComponentProps> = ({ title }) => {
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold">{title}</h2>
    </div>
  );
};
```

### API Integration

Use the API client in `src/services/api.ts`:

```tsx
import { projectsApi } from '@/services/api';

// In your component
const fetchProjects = async () => {
  const response = await projectsApi.getAll();
  return response.data;
};
```

### Styling with Tailwind

Use Tailwind utility classes:

```tsx
<div className="bg-gray-800 rounded-lg shadow-xl p-8">
  <h1 className="text-2xl font-bold text-white">Title</h1>
</div>
```

## Phase 0 Status

✅ **Complete!**

- React app initialized with Vite
- TypeScript configured
- Tailwind CSS set up
- Basic component structure created
- API client skeleton ready
- Type definitions created

## Next Steps (Phase 2)

Phase 2 will implement:
- Interactive dependency graph with React Flow
- Graph controls (zoom, pan, search)
- Node details panel
- Graph filtering and highlighting

## Troubleshooting

### Port Already in Use

If port 5173 is already in use:

```bash
# Kill the process using the port
lsof -ti:5173 | xargs kill -9

# Or use a different port
npm run dev -- --port 3000
```

### Module Not Found Errors

If you get module not found errors:

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors

TypeScript errors are expected until dependencies are installed:

```bash
npm install
```

The errors will resolve once all packages are installed.

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

Access in code:
```tsx
const apiUrl = import.meta.env.VITE_API_URL;
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

When adding new features:
1. Create components in appropriate directories
2. Add TypeScript types in `src/types/`
3. Use Tailwind for styling
4. Follow existing code patterns
5. Test in development mode before building

## Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [React Flow Docs](https://reactflow.dev/)