import re
import random
from datetime import datetime

class EyeCareChatbot:
    def __init__(self):
        self.name = "Dr. EyeBot"
        self.knowledge_base = {
            'dry_eyes': {
                'symptoms': "Burning, itching, redness, blurred vision that improves with blinking",
                'causes': "Screen time, dry environments, aging, medications, autoimmune conditions",
                'precautions': [
                    "Use artificial tears regularly",
                    "Follow 20-20-20 rule for screen time",
                    "Use humidifier in dry environments",
                    "Wear wrap-around sunglasses outdoors"
                ],
                'foods': [
                    "Omega-3 rich foods (salmon, flaxseeds, walnuts)",
                    "Vitamin A foods (carrots, sweet potatoes)",
                    "Hydrating foods (cucumber, watermelon)"
                ],
                'treatments': [
                    "OTC: Artificial tears (Systane, Refresh)",
                    "Rx: Cyclosporine (Restasis), Lifitegrast (Xiidra)",
                    "Procedures: Punctal plugs"
                ],
                'glasses': "Moisture chamber glasses for severe cases"
            },
            
            'red_eyes': {
                'symptoms': "Redness, irritation, possible discharge",
                'causes': "Allergies, infections, dryness, irritation",
                'precautions': [
                    "Avoid rubbing eyes",
                    "Use cool compresses",
                    "Replace eye makeup regularly",
                    "Wash hands frequently"
                ],
                'foods': [
                    "Anti-inflammatory foods (berries, leafy greens)",
                    "Vitamin C foods (oranges, bell peppers)",
                    "Zinc-rich foods (nuts, seeds)"
                ],
                'treatments': [
                    "Allergies: Antihistamine drops (Zaditor)",
                    "Infection: Antibiotic drops (only if bacterial)",
                    "Dryness: Lubricating drops"
                ],
                'glasses': "No special glasses needed unless photophobia exists"
            },
            
            'cataracts': {
                'symptoms': "Cloudy vision, glare sensitivity, fading colors",
                'causes': "Aging, UV exposure, diabetes, trauma, smoking",
                'precautions': [
                    "Wear UV-protected sunglasses",
                    "Control blood sugar if diabetic",
                    "Quit smoking",
                    "Eat antioxidant-rich diet"
                ],
                'foods': [
                    "Vitamin C (citrus fruits, berries)",
                    "Vitamin E (nuts, seeds)",
                    "Lutein/zeaxanthin (kale, spinach)",
                    "Omega-3 fatty acids"
                ],
                'treatments': [
                    "Surgery is only effective treatment",
                    "Early stages: Stronger glasses may help"
                ],
                'glasses': "Anti-glare lenses help with glare sensitivity"
            },
            
            'glaucoma': {
                'symptoms': "Often none early; late stages: peripheral vision loss",
                'causes': "High eye pressure, genetics, age, thin corneas",
                'precautions': [
                    "Regular eye pressure checks",
                    "Avoid head-down positions",
                    "Limit caffeine",
                    "Exercise moderately"
                ],
                'foods': [
                    "Leafy greens (nitrates help blood flow)",
                    "Omega-3 foods",
                    "Antioxidant-rich berries"
                ],
                'treatments': [
                    "Prescription drops (Latanoprost, Timolol)",
                    "Laser treatments",
                    "Surgery in advanced cases"
                ],
                'glasses': "No special glasses, but protect eyes from trauma"
            },
            
            'macular_degeneration': {
                'symptoms': "Blurred central vision, distorted lines",
                'causes': "Aging, smoking, genetics, UV exposure",
                'precautions': [
                    "Wear sunglasses with UV protection",
                    "Quit smoking",
                    "Monitor vision with Amsler grid",
                    "Control blood pressure"
                ],
                'foods': [
                    "AREDS2 formula foods (leafy greens, colorful fruits)",
                    "Omega-3 rich fish",
                    "Zinc-rich foods"
                ],
                'treatments': [
                    "AREDS2 supplements",
                    "Anti-VEGF injections for wet form",
                    "Low vision aids"
                ],
                'glasses': "Low vision aids for advanced cases"
            },
            
            'diabetic_retinopathy': {
                'symptoms': "Floaters, blurred vision, vision loss",
                'causes': "Long-term uncontrolled diabetes",
                'precautions': [
                    "Control blood sugar strictly",
                    "Manage blood pressure",
                    "Regular eye exams",
                    "Quit smoking"
                ],
                'foods': [
                    "Low glycemic index foods",
                    "Leafy greens",
                    "Foods rich in vitamins C and E"
                ],
                'treatments': [
                    "Laser treatment",
                    "Anti-VEGF injections",
                    "Vitrectomy in severe cases"
                ],
                'glasses': "Special tinted lenses may help with glare"
            },
            
            'refractive_errors': {
                'symptoms': "Blurry vision (near/far/both), eye strain",
                'types': {
                    'myopia': "Nearsightedness (clear near, blurry far)",
                    'hyperopia': "Farsightedness (clear far, blurry near)",
                    'astigmatism': "Blurry at all distances",
                    'presbyopia': "Age-related near vision loss"
                },
                'precautions': [
                    "Take visual breaks",
                    "Proper lighting for reading",
                    "Regular eye exams"
                ],
                'foods': [
                    "Vitamin A rich foods",
                    "Omega-3 fatty acids",
                    "Antioxidant-rich foods"
                ],
                'treatments': [
                    "Glasses",
                    "Contact lenses",
                    "Refractive surgery (LASIK, PRK)"
                ],
                'glasses': {
                    'myopia': "Concave lenses",
                    'hyperopia': "Convex lenses",
                    'astigmatism': "Cylindrical lenses",
                    'presbyopia': "Reading glasses or progressives"
                }
            },
            
            'general_care': [
                "For healthy eyes: Follow the 20-20-20 rule (every 20 minutes, look 20 feet away for 20 seconds).",
                "Maintain good eye hygiene by washing hands before touching your eyes and replacing eye makeup regularly.",
                "Eat eye-healthy foods like carrots, leafy greens, and fish rich in omega-3 fatty acids."
            ],
            
            'emergencies': [
                "Seek IMMEDIATE medical attention for: Sudden vision loss, severe eye pain, seeing flashes of light with floaters, chemical exposure to eyes",
                "Emergency symptoms: Sudden double vision, bulging eye, eye trauma with bleeding"
            ],
            
            'spectacles': {
                'when_needed': [
                    "You might need glasses if:",
                    "- You have trouble reading small print",
                    "- You squint to see clearly",
                    "- You get headaches after visual work",
                    "- Your vision is blurry at certain distances"
                ],
                'types': [
                    "Common types of spectacles:",
                    "1. Reading glasses (for presbyopia)",
                    "2. Distance glasses (for myopia)",
                    "3. Progressive/bifocals (multiple corrections)",
                    "4. Blue light blocking (for digital strain)"
                ],
                'getting_tested': [
                    "To determine if you need glasses:",
                    "1. Schedule an eye exam with an optometrist",
                    "2. They'll perform a refraction test",
                    "3. You'll try different lens strengths",
                    "4. Get a prescription if needed"
                ]
            },
            
            'medications': {
                'warning': "Never take eye medications without doctor's prescription",
                'common_eye_meds': [
                    "Common eye medications (must be prescribed):",
                    "1. Antibiotic drops (for bacterial infections)",
                    "2. Antihistamine drops (for allergies)",
                    "3. Steroid drops (for inflammation)",
                    "4. Lubricating drops (OTC for dry eyes)"
                ]
            }
        }
        
        # Patterns and responses
        self.patterns = [
            (r'(hi|hello|hey)', self.greet),
            (r'(bye|quit|exit)', self.exit_chat),
            (r'thank', self.thanks),
            (r'(.*dry.*eye.*)|(.*eye.*dry.*)', lambda: self.get_condition_info('dry_eyes')),
            (r'(.*red.*eye.*)|(.*eye.*red.*)|(.*pink.*eye.*)', lambda: self.get_condition_info('red_eyes')),
            (r'(.*glaucoma.*)', lambda: self.get_condition_info('glaucoma')),
            (r'(.*cataract.*)', lambda: self.get_condition_info('cataracts')),
            (r'(.*macular.*)', lambda: self.get_condition_info('macular_degeneration')),
            (r'(.*diabet.*retin.*)', lambda: self.get_condition_info('diabetic_retinopathy')),
            (r'(.*refract.*error.*)|(.*nearsight.*)|(.*farsight.*)|(.*astigmat.*)|(.*presbyop.*)', 
             lambda: self.get_condition_info('refractive_errors')),
            (r'(.*eye.*pain.*)|(.*eye.*hurting.*)|(.*eye.*ache.*)|(.*paining.*eye.*)|(.*eye.*discomfort.*)|(.*my eye hurts.*)', self.eye_pain),
            (r'(.*eye.*hurt.*for.*day.*)|(.*pain.*for.*day.*)', self.eye_pain_duration),
            (r'(.*blur.*vision.*)|(.*can\'t see clearly.*)', self.blurry_vision),
            (r'(.*emergency.*)|(.*urgent.*eye.*)', self.emergency_info),
            (r'(.*spect.*)|(.*glass.*)|(.*lens.*)', self.spectacles_advice),
            (r'(.*tablet.*)|(.*medic.*)|(.*drop.*)', self.medication_advice),
            (r'(.*both.*spect.*medic.*)|(.*spect.*or.*medic.*)', self.spectacles_vs_meds),
            (r'(.*precaut.*)|(.*advice.*)|(.*tips.*)', self.general_precautions),
            (r'(.*food.*)|(.*diet.*)|(.*nutrit.*)', self.general_foods),
            (r'(.*treat.*)', self.general_treatments),
            (r'(.*)', self.default_response)
        ]

    def get_condition_info(self, condition):
        if condition in self.knowledge_base:
            info = self.knowledge_base[condition]
            response = [
                f"=== {condition.replace('_', ' ').upper()} ===",
                f"Symptoms: {info['symptoms']}",
                f"Causes: {info['causes']}",
                "",
                "PRECAUTIONS:",
                *info['precautions'],
                "",
                "RECOMMENDED FOODS:",
                *info['foods'],
                "",
                "TREATMENTS:",
                *info['treatments'],
                ""
            ]
            
            if 'glasses' in info:
                if isinstance(info['glasses'], str):
                    response.append(f"GLASSES RECOMMENDATION: {info['glasses']}")
                else:
                    response.append("GLASSES RECOMMENDATIONS:")
                    for k, v in info['glasses'].items():
                        response.append(f"- {k}: {v}")
            
            return "\n".join(response)
        return self.default_response()

    def spectacles_advice(self):
        specs = self.knowledge_base['spectacles']
        return "\n".join([
            "SPECTACLES/GLASSES ADVICE:",
            *specs['when_needed'],
            "",
            *specs['types'],
            "",
            *specs['getting_tested'],
            "",
            "Note: Only an eye exam can determine if you truly need glasses"
        ])

    def medication_advice(self):
        meds = self.knowledge_base['medications']
        return "\n".join([
            "EYE MEDICATION GUIDANCE:",
            meds['warning'],
            "",
            *meds['common_eye_meds'],
            "",
            "For red/painful eyes:",
            "- Lubricating drops may help dry eyes",
            "- Avoid self-medicating with antibiotics",
            "- See a doctor for proper diagnosis"
        ])

    def spectacles_vs_meds(self):
        return "\n".join([
            "SPECTACLES vs MEDICATION FOR EYE ISSUES:",
            "",
            "You might need SPECTACLES if:",
            "- Your main symptom is blurry vision",
            "- Problems are distance-specific (near/far)",
            "- Symptoms improve with squinting",
            "",
            "You might need MEDICATION if:",
            "- You have redness, discharge, or itching",
            "- Symptoms suggest infection or allergy",
            "- There's swelling or severe irritation",
            "",
            "IMPORTANT:",
            "1. Persistent eye pain/redness needs professional evaluation",
            "2. Never take eye meds without prescription",
            "3. An eye exam can determine the right solution"
        ])
  
    def sugar_related_info(self):
    
        info = self.knowledge_base['sugar_related']
        return "\n".join([
            "=== SUGAR-RELATED EYE ISSUES ===",
            "Effects on eyes:",
            *info['effects'],
            "",
            "Precautions:",
            *info['precautions'],
            "",
            "Recommendations:",
            *info['recommendations']
        ])

    def greet(self):
        greetings = [
            f"Hello! I'm {self.name}, your eye care assistant. How can I help you today?",
            f"Welcome to {self.name}! What eye concerns would you like to discuss?",
            f"Hi there! I'm here to help with your eye health questions. What's on your mind?"
        ]
        return random.choice(greetings)

    def exit_chat(self):
        return "Thank you for chatting. Remember to get regular eye checkups! Goodbye!"

    def thanks(self):
        return "You're welcome! Let me know if you have any other eye health questions."

    def eye_pain(self):
        return "\n".join([
            "Eye Pain Information:",
            "Possible causes:",
            "- Eye strain (from screens or reading)",
            "- Infection (like conjunctivitis)",
            "- Corneal abrasion (scratch on eye surface)",
            "- Glaucoma (emergency if sudden with nausea)",
            "",
            "Suggestions:",
            "1. Rest your eyes",
            "2. Use warm compress for mild pain",
            "3. Avoid rubbing eyes",
            "",
            "When to see a doctor:",
            "- Pain lasts more than 2 days",
            "- Pain is severe",
            "- You have nausea/vomiting",
            "- Vision is suddenly blurry"
        ])

    def blurry_vision(self):
        return "\n".join([
            "Blurry Vision Information:",
            "Common causes:",
            "- Refractive errors (need for glasses)",
            "- Eye strain or fatigue",
            "- Dry eyes",
            "- More serious conditions (cataracts, glaucoma)",
            "",
            "When to worry:",
            "- Sudden blurriness",
            "- Accompanied by eye pain",
            "- Affects only one eye",
            "",
            "Recommendation:",
            "Schedule an eye exam if blurriness persists more than 1-2 days"
        ])

    def emergency_info(self):
        return "\n".join([
            "EYE EMERGENCIES - SEEK CARE IMMEDIATELY FOR:",
            *self.knowledge_base['emergencies'],
            "",
            "If experiencing any of these, go to emergency room or call eye doctor immediately!"
        ])

    def default_response(self):
        return "\n".join([
            "I can provide detailed information about:",
            "- Symptoms and causes of eye conditions",
            "- Precautions and prevention",
            "- Recommended foods and nutrition",
            "- Treatment options",
            "- Glasses recommendations",
            "",
            "Try asking about specific conditions like:",
            "- Dry eyes",
            "- Cataracts",
            "- Glaucoma",
            "- Macular degeneration",
            "- Diabetic retinopathy",
            "- Refractive errors (nearsightedness, etc.)",
            "",
            "Or ask about: precautions, foods, treatments, or glasses"
        ])
        
    def eye_pain_duration(self):
        return "\n".join([
            "For eye pain lasting several days:",
            "This could indicate:",
            "- Persistent eye infection",
            "- Corneal abrasion that isn't healing",
            "- Developing glaucoma (if accompanied by vision changes)",
            "",
            "RECOMMENDATION:",
            "You should see an eye doctor as soon as possible",
            "Persistent eye pain should be examined by a professional",
            "",
            "Until your appointment:",
            "- Avoid rubbing the eye",
            "- Use artificial tears if needed",
            "- Wear sunglasses if light sensitive"
        ])
    
    def general_precautions(self):
        return "\n".join([
            "GENERAL EYE PRECAUTIONS:",
            "1. Follow 20-20-20 rule for digital devices",
            "2. Wear UV-protected sunglasses outdoors",
            "3. Maintain proper lighting when reading",
            "4. Don't rub your eyes",
            "5. Replace contact lenses as recommended",
            "6. Get comprehensive eye exams regularly",
            "7. Control systemic conditions (diabetes, hypertension)",
            "8. Stay hydrated",
            "9. Quit smoking",
            "10. Use protective eyewear for sports/hobbies"
        ])

    def general_foods(self):
        return "\n".join([
            "TOP EYE-HEALTHY FOODS:",
            "1. Leafy greens (kale, spinach) - Lutein/Zeaxanthin",
            "2. Fatty fish (salmon, tuna) - Omega-3",
            "3. Eggs - Lutein, Vitamin E",
            "4. Citrus fruits - Vitamin C",
            "5. Nuts/seeds - Vitamin E",
            "6. Carrots/sweet potatoes - Vitamin A",
            "7. Beef - Zinc",
            "8. Beans - Bioflavonoids, Zinc",
            "9. Water - Hydration",
            "10. Berries - Antioxidants"
        ])

    def general_treatments(self):
        return "\n".join([
            "COMMON EYE TREATMENTS (require professional prescription):",
            "1. Artificial tears - For dry eyes",
            "2. Antibiotic drops - For bacterial infections",
            "3. Antihistamine drops - For allergies",
            "4. Steroid drops - For inflammation",
            "5. Glaucoma medications - To lower eye pressure",
            "6. Anti-VEGF injections - For wet macular degeneration",
            "7. Oral medications - For certain conditions",
            "",
            "WARNING: Never self-medicate for eye problems"
        ])

    def respond(self, user_input):
        for pattern, response_func in self.patterns:
            if re.search(pattern, user_input.lower()):
                return response_func()
        return self.default_response()
    
    def chat(self, user_input):
        """Process user input and return bot response"""
        if not hasattr(self, 'conversation_history'):
            self.conversation_history = []
            
        self.conversation_history.append(("user", user_input))
        response = self.respond(user_input)
        self.conversation_history.append(("bot", response))
        return response


def main():
    bot = EyeCareChatbot()
    print(f"👁️ {bot.name}: {bot.greet()}")
    
    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print(f"👁️ {bot.name}: {bot.exit_chat()}")
            break
            
        response = bot.respond(user_input)
        print(f"👁️ {bot.name}: {response}")

if __name__ == "__main__":
    main()