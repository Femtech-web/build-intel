# BuildIntel

**AI-powered truth engine for discovering stacks, teams, and traction of Web3 projects.**

BuildIntel reveals what technology stack, team composition, and traction metrics crypto and web projects actually use. Built with Next.js, TypeScript, and a neobrutalist design inspired by Covalent's brand system.

## 🎨 Design Philosophy

**Neobrutalism meets Data Intelligence**

- Solid 2px borders with heavy drop shadows
- Sharp grids and modular layouts
- Bold typography with Space Grotesk font
- Vibrant accent colors: Cyan (#00E7FF), Magenta (#FF3F80), Lime (#C7FF00)
- Deep navy background (#0A0F24) for high contrast
- No gradients — pure digital structure

## 🚀 Features

### Landing Page
- Hero section with animated grid background
- Product headline: "Discover What Builders Are Really Using"
- Feature cards highlighting Tech Stack Analysis, Team Insights, and Traction Data
- CTA buttons linking to the scanner tool

### Scanner Tool
- Search bar for project name or URL input
- File upload support (JSON/CSV) - UI ready for backend integration
- "Try Sample Project" buttons with pre-loaded data for Zora, Base, and Friend.Tech
- Matrix-style loader animation during analysis
- Comprehensive results display:
  - **Tech Fingerprint Card**: Frontend, backend, blockchain, and infrastructure
  - **Stats Cards**: GitHub, Funding, Twitter, and Activity metrics
  - **AI Insight Panel**: Sentient ROMA-powered analysis
  - **Export Options**: PNG and PDF export buttons (UI ready)

### About Page
- Mission statement and BuildIntel overview
- Sentient ROMA integration explanation
- Multi-agent intelligence architecture diagram
- Feature breakdown and team section

### Shared Components
- **Header**: Fixed navigation with BuildIntel branding
- **Footer**: "Powered by Sentient ROMA + BuildIntel" with social links
- **AnimatedBackground**: Slowly shifting grid lines with pulsing dots

## 🛠️ Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom neobrutalist utilities
- **Components**: Shadcn/UI
- **Icons**: Lucide React
- **Font**: Space Grotesk (Google Fonts)

## 📁 Project Structure

```
src/
├── app/
│   ├── page.tsx              # Landing page
│   ├── scanner/page.tsx      # Main scanner tool
│   ├── about/page.tsx        # About page
│   ├── layout.tsx            # Root layout
│   ├── globals.css           # Global styles with neobrutalist theme
│   └── api/
│       ├── analyze/route.ts  # Analysis API endpoint
│       └── scan/route.ts     # Scan API endpoint
├── components/
│   ├── Header.tsx            # Navigation header
│   ├── Footer.tsx            # Footer with social links
│   ├── AnimatedBackground.tsx # Animated grid background
│   ├── MatrixLoader.tsx      # Matrix-style loading animation
│   ├── TechFingerprintCard.tsx # Tech stack display
│   ├── StatsCards.tsx        # GitHub, funding, Twitter stats
│   ├── AIInsightPanel.tsx    # AI-generated insights
│   └── ExportButtons.tsx     # Export and share functionality
├── lib/
│   └── mockData.ts           # Sample project data
└── types/
    └── index.ts              # TypeScript interfaces
```

## 🎯 Sample Projects

The app includes mock data for three sample projects:

1. **Zora** - NFT creator platform
2. **Base** - Coinbase's Ethereum L2
3. **Friend.Tech** - Social token platform

## 🔌 API Integration

The frontend is ready for backend integration with two API endpoints:

### POST /api/analyze
Analyzes a project by name or URL
```json
{
  "projectName": "zora",
  "url": "https://zora.co"
}
```

### GET /api/scan
Lists available sample projects

Both endpoints currently return mock data and are ready to connect to a NestJS backend.

## 🎨 Custom CSS Classes

**Neobrutalist utilities** (defined in `globals.css`):

- `.brutal-card` - Card with 2px border and 8px shadow
- `.brutal-button` - Button with 2px border and 4px shadow
- `.brutal-input` - Input with 2px border and shadow
- `.glow-cyan` - Cyan text shadow
- `.glow-magenta` - Magenta text shadow
- `.glow-lime` - Lime text shadow

**Custom color utilities**:

- `bg-navy`, `text-navy` - #0A0F24
- `bg-cyan`, `text-cyan` - #00E7FF
- `bg-magenta`, `text-magenta` - #FF3F80
- `bg-lime`, `text-lime` - #C7FF00
- `text-text-secondary` - #B0B8C2
- `border-brutal-border` - #E8E8E8

## 🚀 Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## 📱 Responsive Design

The app is fully responsive with mobile-first design:
- Stacked layouts on mobile
- Grid layouts on tablet and desktop
- Touch-friendly buttons and inputs
- Optimized animations for performance

## 🎬 Animations

- **Landing page**: Animated grid background with pulsing dots
- **Scanner tool**: Matrix-style loader during analysis
- **Results**: Staggered slide-in animations for cards
- **Hover effects**: Subtle transforms with shadow depth changes

## 🔮 Future Enhancements

- Real-time data fetching from GitHub, Crunchbase, and Twitter APIs
- File upload processing for batch analysis
- PNG/PDF export functionality
- Project comparison tool
- Historical trend analysis
- Custom report generation

## 📄 License

Built for the Web3 community with transparency and data-driven insights.

---

**Powered by Sentient ROMA + BuildIntel** 🚀