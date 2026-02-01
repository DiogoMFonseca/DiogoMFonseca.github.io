# 🚀 Quick Start Guide - Frontend

## 📋 Prerequisites
- Python 3.x (for local testing)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🖥️ Testing the Frontend Locally

### Option 1: Using the included server script (Recommended)

```bash
# Navigate to project directory
cd /Users/diogofonseca/DiogoWeb/DiogoMFonseca.github.io

# Start the server
python server.py

# Open your browser and go to:
# http://localhost:8000
```

### Option 2: Using Python's built-in HTTP server

```bash
# Navigate to project directory
cd /Users/diogofonseca/DiogoWeb/DiogoMFonseca.github.io

# Start server (Python 3)
python -m http.server 8000

# Or (Python 2)
python -m SimpleHTTPServer 8000

# Open your browser and go to:
# http://localhost:8000
```

### Option 3: Using Node.js http-server

```bash
# Install http-server globally (once)
npm install -g http-server

# Navigate to project directory
cd /Users/diogofonseca/DiogoWeb/DiogoMFonseca.github.io

# Start server
http-server -p 8000

# Open your browser and go to:
# http://localhost:8000
```

## 🧪 Testing with Sample Data

The frontend is configured to automatically load test data from `data/test_events.json` if available.

To switch between test and production data, edit `js/main.js`:

```javascript
// In js/main.js, line 7-10:
const CONFIG = {
    dataUrl: 'data/events.json',       // Production data
    testDataUrl: 'data/test_events.json'  // Test data
};
```

The script tries to load test data first, then falls back to production data.

## 📱 Frontend Features

### 1. **Statistics Dashboard**
- Total events count
- Events this month
- Number of sources
- Days until next event

### 2. **Interactive Calendar** (FullCalendar)
- Month view
- Week view
- List view
- Color-coded by source
- Click events for details

### 3. **Event List**
- Chronologically sorted
- Event cards with images
- Source badges
- Category tags
- Click to view details

### 4. **Filtering**
- Filter by source
- Dynamic filter buttons
- Updates both calendar and list

### 5. **Event Modal**
- Full event details
- Event image
- Date, location, source
- Direct link to event page

## 🎨 Customization

### Colors
Edit the color scheme in `index.html` (lines 18-22):

```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #e74c3c;
}
```

### Source Colors
Edit source colors in `js/main.js` (lines 17-24):

```javascript
const SOURCE_COLORS = {
    'Teatro Aveirense': '#e74c3c',
    'GrETUA': '#3498db',
    'Avenida Café': '#f39c12',
    'VIC Aveiro': '#9b59b6',
    'default': '#95a5a6'
};
```

## 🌐 Deploying to GitHub Pages

### Automatic Deployment

GitHub Pages automatically serves from the root of your repository:

1. **Push your changes:**
   ```bash
   git add index.html js/main.js data/
   git commit -m "Add frontend with FullCalendar"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to repository Settings
   - Navigate to "Pages"
   - Source: Deploy from branch `main` / root
   - Save

3. **Access your site:**
   - URL: `https://diogomfonseca.github.io`
   - Wait 1-2 minutes for deployment

### Manual Configuration

If you need a custom domain or different setup:

1. Go to **Settings → Pages**
2. Choose your source (main branch, root or /docs folder)
3. Optionally add a custom domain
4. Enable HTTPS

## 📂 File Structure

```
├── index.html              # Main HTML page
├── js/
│   └── main.js            # JavaScript logic
├── data/
│   ├── events.json        # Production data (from scraper)
│   └── test_events.json   # Test data
└── server.py              # Local development server
```

## 🔧 Troubleshooting

### Events not loading?
1. Check browser console (F12) for errors
2. Verify `data/test_events.json` exists
3. Check CORS if serving from file://
4. Use the provided server script

### Calendar not displaying?
1. Clear browser cache
2. Check internet connection (CDN dependencies)
3. Verify FullCalendar CDN is accessible

### Styling issues?
1. Check Bootstrap CDN is accessible
2. Clear browser cache
3. Try incognito/private mode

## 📱 Mobile Responsive

The frontend is fully responsive:
- Bootstrap grid system
- Mobile-first design
- Touch-friendly event cards
- Responsive calendar views

## 🎯 Next Steps

1. **Test locally:** `python server.py`
2. **Customize colors** to match your branding
3. **Add more scrapers** to increase event sources
4. **Deploy to GitHub Pages**
5. **Share** with the Aveiro community! 🎉

---

**Need help?** Check the browser console for errors or open an issue on GitHub.
