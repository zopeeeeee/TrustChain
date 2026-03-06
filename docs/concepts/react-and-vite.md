# React and Vite

## What is React?

React is a JavaScript library for building **user interfaces**. Created by Meta (Facebook) in 2013, it is the most widely used frontend library in the world. Instagram, Netflix, Airbnb, and thousands of other applications are built with React.

### The Core Idea: Components

React's fundamental idea is that a user interface can be broken down into **components** -- small, reusable, self-contained pieces. Each component manages its own appearance and behavior.

Think of building a UI like building with LEGO bricks:

- A **Button** is a brick -- it knows how to look and what to do when clicked
- A **SearchBar** is a brick -- it has an input field and a submit action
- A **ResultCard** is a brick -- it displays a verdict, confidence bar, and scores
- A **Page** is an assembly of bricks -- the Results page combines multiple cards

Each brick (component) is independent. You can reuse the same Button component on every page. If you change how Button looks, every page using it updates automatically.

### How TrustChain-AV Uses Components

TrustChain-AV's frontend is organized into components:

**Pages** (full screens):
- **HomePage**: Dashboard with quick stats (total analyses, real count, fake count)
- **UploadPage**: Drag-and-drop video upload with progress tracking
- **ResultsPage**: Multi-card display of analysis verdict, scores, and metadata
- **HistoryPage**: Paginated table of all past analyses with search and filtering

**Shared components**:
- Navigation bar (appears on every page)
- Buttons, cards, badges (used across multiple pages)

### State: How Components Remember Things

Components can have **state** -- data that can change over time. When state changes, React automatically updates what the user sees.

Examples in TrustChain-AV:
- The upload page tracks whether a file is currently uploading (state: `uploading: true/false`)
- The results page tracks whether the PDF is being generated (state: `pdfLoading: true/false`)
- The history page tracks which rows are expanded (state: `expandedIds: Set of IDs`)

When `pdfLoading` changes from `false` to `true`, the download button automatically switches from "Download PDF" to "Generating..." with a spinner. React handles this automatically -- you just update the state, and the UI follows.

### Hooks: Reusable Logic

**Hooks** are functions that let components use features like state, effects (side actions), and more. TrustChain-AV uses several custom hooks:

- **useJobStatus**: Polls the backend for an analysis job's current status and results
- **useHistory**: Fetches the paginated list of past analyses with search and filter parameters

Hooks let you extract and share logic between components. Instead of writing the same "fetch and poll" logic in every page that needs it, you write it once as a hook and use it wherever needed.

## What is Vite?

Vite (French for "fast") is a **build tool** for modern web applications. Created by Evan You (who also created Vue.js), Vite has become the most popular build tool for React projects, replacing older tools like Create React App and Webpack.

### Why a Build Tool is Needed

Browsers understand HTML, CSS, and JavaScript. But modern web applications are written in:

- **TypeScript** (a typed version of JavaScript) -- browsers do not understand it directly
- **JSX** (JavaScript with HTML-like syntax) -- browsers do not understand it directly
- **CSS modules or Tailwind** (modern CSS tooling) -- needs processing
- **Import statements** (organizing code into files) -- needs bundling for production

A build tool transforms your source code into something browsers can run.

### What Vite Does

**During development** (when you run `npm run dev`):
- Starts a development server instantly (no waiting for a full build)
- Uses **Hot Module Replacement (HMR)**: When you save a file, only the changed component updates in the browser -- the page does not fully reload. If you are looking at the results page and change its styling, the change appears in under a second without losing your current state.

**For production** (when you run `npm run build`):
- Bundles all your code into optimized files
- Minifies JavaScript (removes whitespace, shortens variable names) to reduce file size
- Tree-shakes unused code (if you import a library but only use one function, only that function is included)
- Splits code into chunks (pages load their own code on-demand, not everything upfront)

### Why Vite is Fast

Traditional bundlers (like Webpack) process your entire application on every change. If you have 1,000 files and change one, Webpack re-processes many of them.

Vite takes a different approach:
- During development, it serves files individually using native ES modules (the browser fetches only what it needs)
- It only transforms files when the browser requests them
- Changes are near-instantaneous because only the changed file is reprocessed

Think of it as the difference between reprinting an entire book when you fix a typo (Webpack) vs. reprinting just the one page (Vite).

## TypeScript: JavaScript with Safety

TrustChain-AV is written in **TypeScript**, not plain JavaScript. TypeScript adds **type checking** -- it verifies at development time that your code uses data correctly.

For example, if the API returns a confidence score as a number between 0 and 1, TypeScript ensures you never accidentally treat it as a string or forget to handle the case where it is null. These errors are caught before the code runs, not when a user encounters a crash.

Think of TypeScript as spell-check for code. It does not change what you can write -- it just warns you when something does not make sense.

## Tailwind CSS: Styling Without Stylesheets

Instead of writing separate CSS files with class names like `.results-card { background: white; padding: 24px; border-radius: 8px; }`, Tailwind CSS lets you apply styles directly in the HTML using utility classes:

```
bg-white p-6 rounded-lg
```

Each class does one thing:
- `bg-white` = white background
- `p-6` = padding of 1.5rem (24px)
- `rounded-lg` = large border radius

### Why Tailwind?

- **No naming**: You never need to invent class names like `.results-card-header-wrapper`
- **No switching files**: Styles are right next to the elements they affect
- **Consistent spacing**: Tailwind's spacing scale (1, 2, 3, 4, 6, 8, 12...) keeps the design consistent
- **Responsive design**: Prefix any class with `md:` for medium screens, `lg:` for large screens
- **Small final CSS**: Tailwind only includes the classes you actually use in the production build

TrustChain-AV uses Tailwind CSS v4, which integrates with Vite through a plugin (`@tailwindcss/vite`) -- no separate configuration file needed.

## React Router: Navigation Between Pages

A traditional website loads a new HTML page from the server when you click a link. This causes a full page reload -- the screen goes white briefly while the new page loads.

**React Router** enables **client-side routing** -- when you click a link, React instantly swaps the current page component for the new one without a full reload. The URL changes, but the browser never actually loads a new page from the server.

TrustChain-AV's routes:
- `/` -- HomePage (dashboard)
- `/upload` -- UploadPage
- `/results/:id` -- ResultsPage (the `:id` is a dynamic parameter -- each analysis has its own URL)
- `/history` -- HistoryPage

Navigating between these pages is instant. The navigation bar stays in place, and only the page content changes.

## How the Frontend Talks to the Backend

The React frontend communicates with the FastAPI backend through **HTTP requests** using the Fetch API:

1. Frontend calls a function like `getUploads({ page: 1, search: "interview" })`
2. This sends an HTTP GET request to `http://localhost:8000/api/uploads?page=1&search=interview`
3. The backend processes the request and returns JSON data
4. The frontend receives the data and updates the UI

All API functions are centralized in a single file (`api.ts`), so if the API URL changes, only one file needs updating.

### Polling for Status

When a video is being analyzed, the frontend needs to check for updates. It does this through **polling** -- repeatedly asking the backend "Is it done yet?" at regular intervals (every 2 seconds).

The `useJobStatus` hook handles this:
1. Fetch the current status
2. If the status is "completed" or "failed," stop polling
3. Otherwise, wait 2 seconds and fetch again

This continues until the analysis finishes, at which point the results are displayed.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Component** | A self-contained, reusable piece of UI |
| **State** | Data within a component that can change over time |
| **Hook** | A function that lets components use React features (state, effects, etc.) |
| **JSX** | JavaScript syntax extension that looks like HTML |
| **TypeScript** | JavaScript with type safety (catches errors before runtime) |
| **Vite** | A fast build tool for development and production |
| **HMR** | Hot Module Replacement -- instant updates without full page reload |
| **Tailwind CSS** | Utility-first CSS framework (styles via class names) |
| **React Router** | Client-side navigation between pages without full reloads |
| **Polling** | Repeatedly checking for updates at regular intervals |
| **API client** | Centralized functions for communicating with the backend |

## Further Reading

- [FastAPI](fastapi.md) -- The backend API that the frontend communicates with
- [Docker and Containerization](docker-and-containerization.md) -- How the frontend runs in a container
