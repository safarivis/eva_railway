# EVA UI Theme Guidelines
## Modern Minimalist Design System

*"Simplicity is the ultimate sophistication" - Leonardo da Vinci*

---

## 🎨 **Design Philosophy**

### Core Principles
- **Minimalism**: Every element serves a purpose
- **Elegance**: Clean, refined, sophisticated aesthetics
- **Functionality**: Form follows function, never the reverse
- **Consistency**: Unified visual language across all interfaces
- **Accessibility**: Clear, readable, intuitive for all users

### Steve Jobs Inspired Approach
- **Less is More**: Remove unnecessary elements relentlessly
- **Focus on Details**: Perfect the small things that matter
- **Human-Centered**: Design for real people solving real problems
- **Emotional Connection**: Create beautiful, delightful experiences
- **Quality over Quantity**: Better to do fewer things exceptionally well

---

## 🌑 **Color Palette**

### Primary Colors
```css
/* Pure Black Background */
background: #000;

/* Pure White Text */
color: #fff;

/* Essential Greys Only */
--grey-100: #888;  /* Secondary text, placeholders */
--grey-200: #666;  /* Disabled states, timestamps */
--grey-300: #555;  /* Subtle accents */
--grey-400: #444;  /* Borders, dividers */
```

### Forbidden Colors
```css
/* NEVER USE THESE */
--blue: #007AFF;     /* ❌ Too colorful, distracting */
--red: #FF3B30;      /* ❌ Aggressive, alarming */
--orange: #FF9F0A;   /* ❌ Playful, unprofessional */
--green: #00FF00;    /* ❌ Childish, unrefined */
--purple: #5856D6;   /* ❌ Unnecessary decoration */
```

### Transparency Layers
```css
/* Glass Morphism Effects */
--glass-1: rgba(255, 255, 255, 0.02);   /* Subtle cards */
--glass-2: rgba(255, 255, 255, 0.05);   /* Interactive elements */
--glass-3: rgba(255, 255, 255, 0.08);   /* Hover states */
--glass-4: rgba(255, 255, 255, 0.1);    /* Active elements */
--glass-5: rgba(255, 255, 255, 0.15);   /* Prominent buttons */

/* Border Transparencies */
--border-1: rgba(255, 255, 255, 0.05);  /* Subtle divisions */
--border-2: rgba(255, 255, 255, 0.1);   /* Card borders */
--border-3: rgba(255, 255, 255, 0.2);   /* Active borders */
--border-4: rgba(255, 255, 255, 0.3);   /* Focus states */
```

---

## 📝 **Typography**

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', sans-serif;
```

### Text Hierarchy
```css
/* Large Headers */
.title-large {
    font-size: 3rem;
    font-weight: 300;
    letter-spacing: -0.02em;
    line-height: 1.1;
}

/* Section Headers */
.title-medium {
    font-size: 1.5rem;
    font-weight: 500;
    letter-spacing: -0.01em;
    line-height: 1.2;
}

/* Card Titles */
.title-small {
    font-size: 1.1rem;
    font-weight: 500;
    line-height: 1.3;
}

/* Body Text */
.body-text {
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
}

/* Secondary Text */
.caption {
    font-size: 0.8rem;
    font-weight: 400;
    color: #888;
    line-height: 1.4;
}

/* Code/Monospace */
.code {
    font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
    font-size: 0.8rem;
    line-height: 1.3;
}
```

---

## 🔲 **Layout & Spacing**

### Grid System
```css
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 24px;
}
```

### Spacing Scale
```css
/* 8px base unit */
--space-1: 8px;    /* 8px */
--space-2: 16px;   /* 16px */
--space-3: 24px;   /* 24px */
--space-4: 32px;   /* 32px */
--space-5: 40px;   /* 40px */
--space-6: 48px;   /* 48px */
--space-8: 64px;   /* 64px */
--space-10: 80px;  /* 80px */
```

---

## 🎛️ **Components**

### Cards
```css
.card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(20px);
    transition: all 0.2s ease;
}

.card:hover {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.2);
}
```

### Buttons
```css
.btn {
    padding: 14px 28px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.05);
    color: #fff;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    backdrop-filter: blur(20px);
}

.btn:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
}

.btn.primary {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.3);
}
```

### Input Fields
```css
.input {
    padding: 16px 20px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    color: #fff;
    font-size: 1rem;
    outline: none;
    transition: all 0.2s ease;
}

.input:focus {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.3);
}

.input::placeholder {
    color: #666;
}
```

### Toggle Switches
```css
.toggle-switch {
    width: 44px;
    height: 24px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    position: relative;
    cursor: pointer;
    transition: background 0.2s ease;
}

.toggle-switch.active {
    background: rgba(255, 255, 255, 0.3);
}

.toggle-switch::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    background: #fff;
    border-radius: 50%;
    top: 2px;
    left: 2px;
    transition: transform 0.2s ease;
}

.toggle-switch.active::after {
    transform: translateX(20px);
}
```

---

## ✨ **Animations & Transitions**

### Standard Timing
```css
/* Quick interactions */
transition: all 0.2s ease;

/* Content changes */
transition: all 0.3s ease;

/* Page transitions */
transition: all 0.4s ease;
```

### Micro-Interactions
```css
/* Fade in animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Pulse animation for live indicators */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Subtle hover lift */
.interactive:hover {
    transform: translateY(-1px);
}
```

---

## 📱 **Responsive Design**

### Breakpoints
```css
/* Mobile */
@media (max-width: 768px) {
    .container {
        padding: 20px 16px;
    }
    
    .grid {
        grid-template-columns: 1fr;
        gap: 16px;
    }
    
    .title-large {
        font-size: 2.5rem;
    }
}

/* Tablet */
@media (max-width: 1024px) {
    .container {
        padding: 30px 20px;
    }
}
```

---

## 🎯 **Implementation Examples**

### Chat Interface (Working Reference)
```html
<!-- Modern minimalist chat interface -->
<div class="chat-container">
    <div class="messages" id="messages">
        <div class="message user">
            Hello EVA, can you help me?
        </div>
        <div class="message eva">
            Of course! I'm here to help. What do you need assistance with?
        </div>
    </div>
    
    <div class="input-container">
        <input type="text" class="message-input" placeholder="Type your message...">
        <button class="send-btn">Send</button>
    </div>
</div>
```

### Dashboard Cards (Working Reference)
```html
<!-- Clean dashboard layout -->
<div class="grid">
    <div class="card">
        <h3>💰 Cost Overview</h3>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">$0.24</div>
                <div class="metric-label">Today</div>
            </div>
        </div>
    </div>
</div>
```

---

## ❌ **What NOT to Do**

### Visual Anti-Patterns
- **No bright colors**: Blue buttons, red errors, green success states
- **No gradients**: Except subtle white transparency gradients
- **No shadows**: Use backdrop-blur instead of box-shadow
- **No icons**: Unless absolutely necessary for clarity
- **No rounded corners > 16px**: Keep it subtle and refined
- **No animations > 0.4s**: Fast, responsive interactions only

### Content Anti-Patterns
- **No emoji overuse**: One per section maximum
- **No marketing language**: Clear, direct, honest communication
- **No unnecessary text**: Every word must serve a purpose
- **No technical jargon**: Simple, human language

---

## ✅ **Quality Checklist**

### Before Shipping Any UI
- [ ] Only black, white, and grey colors used
- [ ] Typography follows hierarchy consistently
- [ ] All interactive elements have hover states
- [ ] Spacing follows 8px grid system
- [ ] Responsive design works on mobile
- [ ] Animations are subtle and purposeful
- [ ] Content is clear and concise
- [ ] Glass morphism effects are applied consistently
- [ ] No unnecessary visual elements
- [ ] Accessibility considerations met

---

## 🏆 **Success Metrics**

### User Experience Goals
- **Immediate comprehension**: Users understand interface instantly
- **Effortless interaction**: No learning curve required
- **Emotional satisfaction**: Users feel calm, focused, empowered
- **Performance**: Interfaces feel fast and responsive
- **Consistency**: Users know what to expect everywhere

### Design Quality Indicators
- **Visual hierarchy is clear**: Most important elements stand out naturally
- **White space is purposeful**: Every space serves readability or focus
- **Color draws attention correctly**: White text on black background, nothing else competing
- **Interactions feel natural**: Buttons respond as expected, feedback is immediate
- **Content is scannable**: Users can quickly find what they need

---

## 📚 **References & Inspiration**

### Design Philosophy Sources
- Apple Human Interface Guidelines
- Dieter Rams' 10 Principles of Good Design
- Swiss Typography Movement
- Bauhaus Design School
- Japanese Minimalism (Wabi-Sabi)

### Technical Implementation
- Modern CSS Grid and Flexbox
- CSS Custom Properties (Variables)
- Backdrop-filter for glass effects
- System font stacks for performance
- Progressive enhancement principles

---

*"Design is not just what it looks like and feels like. Design is how it works."*  
**- Steve Jobs**

---

**Document Version:** 1.0  
**Last Updated:** June 5, 2025  
**Author:** Claude Code Assistant  
**Status:** ✅ Production Ready