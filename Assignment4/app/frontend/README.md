# QueryWorks 2.0 Frontend

The frontend module is built using React to provide a responsive and reactive interface. It interacts heavily with our partitioned backend relying on our defined Sharding APIs.

## File Breakdown

* **`index.html`**: Entry point for rendering the app. Defines metadata and injects the core `App` component into the DOM.
* **`index.tsx` / `App.tsx`**: Bootstraps the application. Contains the root routing wrapper allowing users to navigate between available rides, chat interface, history view, admin dashboard, etc. 
* **`store.tsx`**: Global state management configuration. Stores session states like user context (ID, Role), map coordinates, and UI themes across pages correctly tracking active ride flows.
* **`package.json`**: Describes application dependencies, including Next/React router dependencies, styling plugins, or chart toolkits. Contains package scripts like `dev`, `build`, and `preview`.
* **`vite.config.ts`**: The bundler configuration script. This runs the build pipeline efficiently parsing TSX assets.
* **`.env`**: Contains sensitive keys holding references to the backend base API URL across different environments.
* **`tsconfig.json`**: Rules dictating how TypeScript handles type checking, defining generic parameters across components and DOM libraries.
* **`types.ts`**: Core TypeScript interfaces shared between files for type safety. Defines expected payload schemas for models such as `Ride`, `User`, `Message`, and mapping these responses back seamlessly from the sharded API requests.
* **`components/`**: Reusable view logic segments such as navigations (`Navbar.tsx`), dynamic input logic (`Autocomplete.tsx`), custom maps (`MapComponent.tsx`), and restricted interfaces (`AdminRoute.tsx`).
* **`pages/`**: Single-pane routing modules serving as full-screen interfaces. For example, `Profile.tsx`, `AddRide.tsx`, `AvailableRides.tsx`.

## How to Run (from the repository root directory)

Open your terminal at the root directory of Assignment 4 (`Assignment4/`), then run:

### Setup & Activation

1. **Install dependencies:**
   Make sure you have Node.js and npm installed. Run the command to install packages:
   ```bash
   npm install 
   ```

2. **Start the development server:**
   Use the `npm run dev` script targeted at the frontend prefix.
   ```bash
   npm run dev
   ```
