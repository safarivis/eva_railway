# Appointment Booking with Eva

Eva now provides intelligent appointment booking assistance, creating comprehensive call scripts and guidance to help you book appointments seamlessly and professionally.

## 🎯 Key Features

### 📋 Comprehensive Call Preparation
- **Detailed call scripts** with professional openings and conversation flow
- **Expected questions** businesses typically ask
- **Information preparation** checklists
- **Backup options** for common scenarios
- **Professional conversation templates**

### 🏥 Specialized Support for Different Appointment Types
- **Doctor appointments**: Medical-specific questions and requirements
- **Dental appointments**: Dental care scheduling with insurance prep
- **Haircut/salon**: Beauty service booking with stylist preferences  
- **General appointments**: Flexible template for any business

### 🎤 Audio Support (Optional)
- Generate audio versions of call scripts using ElevenLabs TTS
- Professional voice guidance for appointment calls
- Audio preparation briefings

## 🚀 How to Use

### Quick Start
Simply ask Eva to help with appointment booking:

```
"Help me book a doctor's appointment for next Monday"
"I need to schedule a dental cleaning"
"Book me a haircut appointment this week"
"Help me call and make an appointment at [business name]"
```

### Detailed Example
```
User: "I need to book a dentist appointment at Downtown Dental Clinic. 
       Their number is (555) 123-4567. I prefer mornings next week."

Eva: I'll help you prepare for that dental appointment call!
     [Creates comprehensive call script with all the details]
```

## 📞 What Eva Provides

### 1. Professional Call Script
- **Opening greeting** with proper introduction
- **Appointment details** clearly organized
- **Conversation flow** guide
- **Key information** to provide
- **Professional closing**

### 2. Preparation Checklist
- Information you'll need to have ready
- Common questions to expect
- Backup scheduling options
- Special requirements to mention

### 3. Conversation Tips
- How to handle scheduling conflicts
- Professional language to use
- What to ask for confirmation
- Follow-up information to get

## 💼 Appointment Types Supported

### 🏥 Medical Appointments
**Typical Duration**: 30-60 minutes  
**Advance Booking**: 1-2 weeks  
**Info Needed**: Name, insurance, reason for visit, preferred doctor

**Common Questions**:
- What type of appointment?
- Insurance information?
- Reason for visit?
- Preferred doctor?

### 🦷 Dental Appointments  
**Typical Duration**: 30-90 minutes  
**Advance Booking**: 2-4 weeks  
**Info Needed**: Name, insurance, last visit, service type

**Common Questions**:
- Cleaning or specific issue?
- Preferred dentist/hygienist?
- Insurance information?
- When was your last visit?

### ✂️ Haircut/Salon Appointments
**Typical Duration**: 30-120 minutes  
**Advance Booking**: 1-2 weeks  
**Info Needed**: Name, service type, stylist preference

**Common Questions**:
- Preferred stylist?
- Type of service?
- Specific requests or styles?

### 🏢 General Business Appointments
**Typical Duration**: 30-60 minutes  
**Advance Booking**: 1-2 weeks  
**Info Needed**: Name, appointment type, duration

## 📝 Example Call Script

Here's what Eva creates for you:

```
📞 APPOINTMENT BOOKING CALL SCRIPT FOR Downtown Dental Clinic
Phone: (555) 123-4567

=== OPENING ===
"Hi, good morning! My name is Eva and I'm calling on behalf of 
Louis du Plessis to schedule a dental appointment."

=== APPOINTMENT DETAILS ===
• Client Name: Louis du Plessis
• Appointment Type: 30-90 minutes dental appointment
• Reason: Routine cleaning and checkup
• Duration Needed: Approximately 30-90 minutes

=== PREFERRED SCHEDULING ===
• Preferred Dates: next Monday, next Tuesday
• Preferred Times: morning, early afternoon
• Special Requests: prefer morning appointments if available

=== TYPICAL QUESTIONS THEY MIGHT ASK ===
• Is this for a cleaning or specific issue?
• Do you have a preferred dentist or hygienist?
• What's your insurance information?
• When was your last visit?
• What times work best for you?

=== BOOKING FLOW ===
1. Introduce yourself and state purpose
2. Provide client name and appointment type
3. Share preferred dates/times
4. Answer any questions about the appointment
5. Confirm final appointment details
6. Get any preparation instructions
7. Thank them and confirm contact information
```

## 🎯 Smart Features

### Intelligent Information Gathering
Eva automatically extracts and organizes:
- Business name and contact information
- Your preferred dates and times
- Appointment type and specific needs
- Special requests or requirements

### Scenario-Based Preparation
Different scripts and advice for:
- First-time vs. returning patient appointments
- Urgent vs. routine scheduling
- Insurance vs. self-pay situations
- Specific vs. general appointment needs

### Professional Communication
Eva ensures your calls are:
- **Professional** and courteous
- **Clear** and well-organized  
- **Efficient** and respectful of time
- **Thorough** with all necessary details

## 💡 Pro Tips

### Before You Call
1. **Have your calendar ready** with multiple date/time options
2. **Gather required information** (insurance, last visit dates, etc.)
3. **Review the script** Eva provides
4. **Prepare for common questions**
5. **Have backup dates** in case first choices aren't available

### During the Call
1. **Speak clearly** and at a normal pace
2. **Be flexible** with scheduling options
3. **Ask questions** if anything is unclear
4. **Confirm all details** before ending
5. **Get contact information** for follow-up

### After the Call
1. **Mark your calendar** immediately
2. **Set reminders** for the appointment
3. **Note any preparation requirements**
4. **Save contact information** for future reference

## 🛠️ Setup Requirements

### Basic Setup (No additional requirements)
- Eva's appointment booking works out of the box
- No API keys or external services needed for call script generation

### Enhanced Features (Optional)
- **ElevenLabs API Key**: For audio script generation
- Set environment variable: `ELEVENLABS_API_KEY=your_key`

## 📱 Usage Examples

### Simple Request
```
User: "Book me a doctor's appointment"
Eva: I'll help you prepare for that doctor's appointment call! 
     I'll need a few details...
```

### Detailed Request  
```
User: "I need a dental cleaning at Smile Dental, (555) 123-4567, 
       preferably Tuesday morning"
Eva: Perfect! I'll create a comprehensive call script for your 
     dental cleaning appointment at Smile Dental...
```

### Quick Info Request
```
User: "What should I know before calling to book a haircut?"
Eva: Here's what you should prepare for a haircut appointment call...
```

## 🔧 Technical Details

### Files Involved
- `integrations/simple_appointment_handler.py` - Main appointment logic
- `integrations/tool_manager.py` - Tool integration
- `core/eva.py` - System prompt integration
- `tests/test_appointment_booking.py` - Integration tests

### Actions Available
- `prepare_appointment` - Create detailed call script and guidance
- `quick_appointment_info` - Get quick tips for appointment types

### Response Format
```json
{
  "call_script": "Detailed call script text...",
  "appointment_summary": {
    "business_name": "Business Name",
    "appointment_type": "dentist",
    "preferred_dates": ["Monday", "Tuesday"],
    "typical_duration": "30-90 minutes"
  },
  "next_steps": ["Call the business", "Use script as guide", ...]
}
```

## 🎉 Benefits

### For You
- **Professional representation** in all appointment calls
- **Reduced anxiety** with prepared scripts and guidance
- **Better success rates** with organized approach
- **Time savings** with efficient call preparation

### For Businesses
- **Clear communication** of your needs
- **Organized information** provided efficiently
- **Professional interaction** improving their experience
- **Reduced back-and-forth** with thorough preparation

Eva makes appointment booking stress-free and professional, ensuring you get the appointments you need with confidence and ease!