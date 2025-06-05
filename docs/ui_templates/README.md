# EVA UI Templates & Theme System

## 📁 **Template Files**

### Core Files
- `eva_theme.css` - Complete CSS theme system with all components
- `eva_chat_template.html` - Chat interface template 
- `eva_dashboard_template.html` - Dashboard interface template
- `README.md` - This documentation

## 🎨 **Design System**

### Philosophy
Modern minimalist design inspired by Steve Jobs' principles:
- **Pure black/white/grey palette** - No blue, red, orange colors
- **Glass morphism effects** - Subtle transparency layers
- **Typography hierarchy** - Apple system fonts
- **Consistent spacing** - 8px grid system
- **Subtle animations** - Fast, purposeful interactions

### Color Variables
```css
--eva-black: #000;
--eva-white: #fff;
--eva-grey-100: #888;  /* Secondary text */
--eva-grey-200: #666;  /* Disabled states */
--eva-glass-1: rgba(255, 255, 255, 0.02);  /* Cards */
--eva-glass-4: rgba(255, 255, 255, 0.1);   /* Buttons */
```

## 🚀 **Quick Start**

### 1. Use Complete Template
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="eva_theme.css">
</head>
<body>
    <div class="eva-container">
        <h1 class="eva-title-large">EVA</h1>
        <div class="eva-card">
            <p class="eva-body">Your content here</p>
        </div>
    </div>
</body>
</html>
```

### 2. Import Just the CSS
```html
<link rel="stylesheet" href="path/to/eva_theme.css">
```

### 3. Copy Component Classes
Use any `eva-*` class from the theme:
- `eva-btn` - Buttons
- `eva-card` - Container cards  
- `eva-input` - Form inputs
- `eva-toggle` - Toggle switches

## 🧩 **Component Examples**

### Button
```html
<button class="eva-btn eva-btn-primary">Primary Action</button>
<button class="eva-btn">Secondary Action</button>
<button class="eva-btn eva-btn-small">Small Button</button>
```

### Card
```html
<div class="eva-card">
    <h3 class="eva-title-small">Card Title</h3>
    <p class="eva-body">Card content goes here.</p>
</div>
```

### Input Field
```html
<input type="text" class="eva-input" placeholder="Enter text...">
<select class="eva-select">
    <option>Option 1</option>
</select>
```

### Toggle Switch
```html
<div class="eva-toggle">
    <div class="eva-toggle-switch active"></div>
    <div class="eva-toggle-label">Toggle Label</div>
</div>
```

### Chat Message
```html
<div class="eva-message user">User message</div>
<div class="eva-message eva">EVA response</div>
<div class="eva-message system">System message</div>
```

### Metrics Display
```html
<div class="eva-metrics">
    <div class="eva-metric">
        <div class="eva-metric-value">$0.24</div>
        <div class="eva-metric-label">Cost Today</div>
    </div>
</div>
```

## 📱 **Responsive Design**

### Mobile-First Approach
```css
/* Default styles are mobile */
.eva-container {
    padding: var(--eva-space-3) var(--eva-space-2);
}

/* Desktop adjustments */
@media (min-width: 768px) {
    .eva-container {
        padding: var(--eva-space-5) var(--eva-space-3);
    }
}
```

### Grid System
```html
<div class="eva-grid">
    <div class="eva-card">Card 1</div>
    <div class="eva-card">Card 2</div>
    <div class="eva-card eva-card-full-width">Full Width Card</div>
</div>
```

## ⚡ **JavaScript Integration**

### EVA Chat Class
```javascript
class EVAChatInterface {
    constructor() {
        this.initializeElements();
        this.setupEventListeners();
    }
    
    addMessage(type, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `eva-message ${type}`;
        messageDiv.textContent = text;
        this.messages.appendChild(messageDiv);
    }
}
```

### EVA Dashboard Class
```javascript
class EVADashboard {
    constructor() {
        this.loadDashboardData();
        this.startAutoRefresh();
    }
    
    updateMetric(id, value) {
        document.getElementById(id).textContent = value;
    }
}
```

## 🎯 **Working Examples**

### Current EVA Implementations
These templates are based on working code from:
- `realtime_app/templates/index.html` - Chat interface
- `realtime_app/templates/dashboard.html` - Dashboard
- `static/index.html` - Main EVA interface

### Copy & Paste Ready
All templates include:
- ✅ Complete HTML structure
- ✅ Working JavaScript classes
- ✅ Responsive design
- ✅ Accessibility features
- ✅ Event handlers
- ✅ API integration points

## 🚫 **Don't Use**

### Forbidden Colors
```css
/* NEVER USE THESE */
color: #007AFF;  /* Blue */
color: #FF3B30;  /* Red */ 
color: #FF9F0A;  /* Orange */
color: #00FF00;  /* Green */
```

### Bad Patterns
- Box shadows (use backdrop-blur instead)
- Bright colors or gradients
- Complex animations (>0.4s duration)
- Heavy frameworks (keep it vanilla)

## 📋 **Checklist**

### Before Using Template
- [ ] CSS variables are defined
- [ ] System fonts are loaded
- [ ] Backdrop-filter is supported
- [ ] Only black/grey/white colors used
- [ ] Responsive breakpoints tested

### Before Shipping
- [ ] Mobile layout works
- [ ] Hover states respond
- [ ] Text is readable
- [ ] Loading states exist
- [ ] Error handling included

## 🔧 **Customization**

### Adjust Spacing
```css
:root {
    --eva-space-3: 32px; /* Increase from 24px */
}
```

### Modify Transparency
```css
:root {
    --eva-glass-2: rgba(255, 255, 255, 0.08); /* More opaque */
}
```

### Add Custom Components
```css
.eva-custom-component {
    background: var(--eva-glass-2);
    border: 1px solid var(--eva-border-2);
    border-radius: 12px;
    padding: var(--eva-space-2);
}
```

## 📚 **Additional Resources**

- `../UI_THEME_GUIDELINES.md` - Complete design philosophy
- Working EVA interfaces for reference
- Apple Human Interface Guidelines
- Modern CSS Grid documentation

---

**Last Updated:** June 5, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready