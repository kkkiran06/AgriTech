"""
PlantDoctor AI - Plant Disease Detection Engine
Uses MobileNetV2 trained on the PlantVillage dataset (38 disease classes).

Model weights are downloaded once from Hugging Face on first use and cached locally.
If download fails, the system automatically falls back to Demo Simulation Mode.
"""

import os
import io
import json
import hashlib
import logging
import random
from pathlib import Path

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# PlantVillage 38-class label mapping
# ─────────────────────────────────────────────
PLANT_DISEASE_CLASSES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot',
    'Corn_(maize)___Common_rust',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites_Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy',
]

# ─────────────────────────────────────────────
# Human-friendly labels + treatment knowledge base
# ─────────────────────────────────────────────
DISEASE_KNOWLEDGE = {
    'Apple___Apple_scab': {
        'display_name': 'Apple Scab',
        'plant': 'Apple',
        'severity': 'Moderate',
        'symptoms': 'Olive-green to brown scab-like lesions on leaves and fruit surface. Leaves may curl and drop early.',
        'prevention': 'Plant resistant apple varieties. Ensure good air circulation by proper pruning. Rake and destroy fallen leaves.',
        'organic_treatment': 'Apply sulfur-based fungicide or neem oil spray every 7–10 days during wet spring weather.',
        'chemical_treatment': 'Spray Mancozeb 75 WP (2.5 g/L) or Captan 50 WP (3 g/L) at bud break and repeat every 10 days.',
        'color': 'warning',
        'emoji': '🍎',
    },
    'Apple___Black_rot': {
        'display_name': 'Apple Black Rot',
        'plant': 'Apple',
        'severity': 'High',
        'symptoms': 'Brown, water-soaked lesions on leaves. Fruit develops concentric rings and turns black and mummified.',
        'prevention': 'Remove mummified fruits and dead wood. Prune cankers in dry weather and disinfect tools.',
        'organic_treatment': 'Copper-based fungicide spray. Ensure proper sanitation of orchard floor.',
        'chemical_treatment': 'Apply Thiophanate-methyl or Captan 50 WP at petal fall and every 10 days through summer.',
        'color': 'danger',
        'emoji': '🍎',
    },
    'Apple___Cedar_apple_rust': {
        'display_name': 'Apple Cedar Rust',
        'plant': 'Apple',
        'severity': 'Moderate',
        'symptoms': 'Bright orange-yellow spots on upper leaf surface with tube-like growths on undersides.',
        'prevention': 'Remove nearby cedar/juniper trees (alternate hosts). Plant rust-resistant apple varieties.',
        'organic_treatment': 'Sulfur dust applications during early spring bloom.',
        'chemical_treatment': 'Myclobutanil or Propiconazole fungicide sprays from pink bud stage through petal fall.',
        'color': 'warning',
        'emoji': '🍎',
    },
    'Apple___healthy': {
        'display_name': 'Healthy Apple Plant',
        'plant': 'Apple',
        'severity': 'None',
        'symptoms': 'No disease detected. Leaves appear green, firm, and without lesions.',
        'prevention': 'Maintain regular fertilization and irrigation schedule. Monitor for early pest signs.',
        'organic_treatment': 'Preventive neem oil spray monthly during growing season.',
        'chemical_treatment': 'No treatment required. Continue standard orchard management.',
        'color': 'success',
        'emoji': '✅',
    },
    'Corn_(maize)___Common_rust': {
        'display_name': 'Maize Common Rust',
        'plant': 'Maize (Corn)',
        'severity': 'Moderate',
        'symptoms': 'Small, circular to elongated cinnamon-brown pustules on both leaf surfaces. Heavy infection causes yellowing.',
        'prevention': 'Plant rust-resistant maize hybrids. Avoid late planting. Ensure adequate plant spacing.',
        'organic_treatment': 'Spray neem oil (5 ml/L) at first appearance of symptoms. Apply wood ash dust.',
        'chemical_treatment': 'Mancozeb 75 WP (2 g/L) or Zineb 75 WP at early infection stage. Repeat after 10–15 days.',
        'color': 'warning',
        'emoji': '🌽',
    },
    'Corn_(maize)___Northern_Leaf_Blight': {
        'display_name': 'Maize Northern Leaf Blight',
        'plant': 'Maize (Corn)',
        'severity': 'High',
        'symptoms': 'Long (10–15 cm), cigar-shaped gray-green to tan lesions on leaves. Severely infected plants die early.',
        'prevention': 'Use resistant hybrids. Rotate crops. Plow under infected crop debris after harvest.',
        'organic_treatment': 'Trichoderma-based biocontrol agents. Neem cake soil application.',
        'chemical_treatment': 'Propiconazole 25 EC (1 ml/L) or Tebuconazole 250 EC. Spray at first symptom appearance.',
        'color': 'danger',
        'emoji': '🌽',
    },
    'Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot': {
        'display_name': 'Maize Gray Leaf Spot',
        'plant': 'Maize (Corn)',
        'severity': 'High',
        'symptoms': 'Rectangular, tan to gray lesions limited by leaf veins. Lesions run parallel to veins and may coalesce.',
        'prevention': 'Crop rotation. Resistant hybrids. Avoid overhead irrigation which promotes humidity.',
        'organic_treatment': 'Trichoderma viride application. Remove infected crop debris promptly.',
        'chemical_treatment': 'Strobilurin fungicides (Azoxystrobin or Pyraclostrobin) at VT (tasseling) growth stage.',
        'color': 'danger',
        'emoji': '🌽',
    },
    'Corn_(maize)___healthy': {
        'display_name': 'Healthy Maize Plant',
        'plant': 'Maize (Corn)',
        'severity': 'None',
        'symptoms': 'No disease detected. Leaves are uniformly green with no lesions.',
        'prevention': 'Continue balanced NPK fertilization. Monitor soil moisture. Scout for pests weekly.',
        'organic_treatment': 'Preventive Trichoderma soil treatment before sowing.',
        'chemical_treatment': 'No treatment required. Continue standard crop management.',
        'color': 'success',
        'emoji': '✅',
    },
    'Potato___Early_blight': {
        'display_name': 'Potato Early Blight',
        'plant': 'Potato',
        'severity': 'Moderate',
        'symptoms': 'Dark brown, circular spots with yellow halos and concentric rings (target-board pattern) on older leaves.',
        'prevention': 'Use certified disease-free seed tubers. Proper plant spacing. Avoid overhead irrigation.',
        'organic_treatment': 'Copper oxychloride (3 g/L) or neem oil spray at first sign of disease.',
        'chemical_treatment': 'Mancozeb 75 WP (2.5 g/L) or Chlorothalonil 75 WP (2 g/L). Spray every 7–10 days.',
        'color': 'warning',
        'emoji': '🥔',
    },
    'Potato___Late_blight': {
        'display_name': 'Potato Late Blight',
        'plant': 'Potato',
        'severity': 'Critical',
        'symptoms': 'Water-soaked pale greenish spots that turn dark brown/black rapidly. White mold on leaf undersides in humid conditions. Can destroy entire crop.',
        'prevention': 'Plant resistant varieties. Avoid overhead watering. Destroy infected plant material immediately.',
        'organic_treatment': 'Copper-based fungicide spray. Bordeaux mixture (1%). Remove and burn affected plants urgently.',
        'chemical_treatment': 'Metalaxyl+Mancozeb (Ridomil Gold MZ) 2.5 g/L. Apply preventively and repeat every 5–7 days in wet weather.',
        'color': 'danger',
        'emoji': '🥔',
    },
    'Potato___healthy': {
        'display_name': 'Healthy Potato Plant',
        'plant': 'Potato',
        'severity': 'None',
        'symptoms': 'No disease detected. Foliage looks healthy and green.',
        'prevention': 'Monitor regularly for late blight symptoms especially during rainy season.',
        'organic_treatment': 'Preventive copper spray before monsoon season.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
    'Tomato___Early_blight': {
        'display_name': 'Tomato Early Blight',
        'plant': 'Tomato',
        'severity': 'Moderate',
        'symptoms': 'Dark brown concentric ring spots on lower/older leaves. Yellowing around lesions. Defoliation from bottom up.',
        'prevention': 'Crop rotation (3 years). Mulch around plants. Avoid wetting foliage when watering.',
        'organic_treatment': 'Neem oil (5 ml/L) or Trichoderma spray. Remove and destroy infected leaves.',
        'chemical_treatment': 'Mancozeb 75 WP (2.5 g/L) or Iprodione 50 WP. Spray at 7–10 day intervals.',
        'color': 'warning',
        'emoji': '🍅',
    },
    'Tomato___Late_blight': {
        'display_name': 'Tomato Late Blight',
        'plant': 'Tomato',
        'severity': 'Critical',
        'symptoms': 'Large, irregular, water-soaked dark brown patches on leaves, stems, and fruit. White fungal growth on undersides in moist conditions.',
        'prevention': 'Avoid planting near potatoes. Good air circulation. Avoid overhead irrigation.',
        'organic_treatment': 'Copper fungicide spray. Bordeaux mixture. Remove all infected material from field.',
        'chemical_treatment': 'Cymoxanil+Mancozeb or Metalaxyl-M+Mancozeb. Apply at 5–7 day intervals during rainy season.',
        'color': 'danger',
        'emoji': '🍅',
    },
    'Tomato___Bacterial_spot': {
        'display_name': 'Tomato Bacterial Spot',
        'plant': 'Tomato',
        'severity': 'Moderate',
        'symptoms': 'Small, water-soaked, circular spots on leaves turning brown with yellow halos. Fruit shows raised scab-like spots.',
        'prevention': 'Use certified disease-free seeds. Avoid overhead watering. Disinfect farm tools.',
        'organic_treatment': 'Copper-based bactericide spray. Remove infected plant debris.',
        'chemical_treatment': 'Copper oxychloride 50 WP (3 g/L) with Streptomycin Sulphate (200 ppm). Spray every 10 days.',
        'color': 'warning',
        'emoji': '🍅',
    },
    'Tomato___Leaf_Mold': {
        'display_name': 'Tomato Leaf Mold',
        'plant': 'Tomato',
        'severity': 'Moderate',
        'symptoms': 'Pale green to yellow patches on upper leaf surface. Olive-green velvety mold on leaf undersides.',
        'prevention': 'Improve greenhouse/field ventilation. Reduce humidity. Space plants adequately.',
        'organic_treatment': 'Neem oil spray. Remove and destroy heavily infected leaves.',
        'chemical_treatment': 'Mancozeb 75 WP (2 g/L) or Chlorothalonil. Spray at first sign of disease.',
        'color': 'warning',
        'emoji': '🍅',
    },
    'Tomato___Septoria_leaf_spot': {
        'display_name': 'Tomato Septoria Leaf Spot',
        'plant': 'Tomato',
        'severity': 'Moderate',
        'symptoms': 'Small circular spots with dark brown border and lighter gray center. Tiny black dots (pycnidia) visible inside spots.',
        'prevention': 'Crop rotation. Remove plant debris. Avoid overhead irrigation. Stake plants for air circulation.',
        'organic_treatment': 'Copper-based fungicide. Neem oil spray at 7-day intervals.',
        'chemical_treatment': 'Mancozeb, Chlorothalonil, or Azoxystrobin. Begin spraying at first symptom appearance.',
        'color': 'warning',
        'emoji': '🍅',
    },
    'Tomato___Target_Spot': {
        'display_name': 'Tomato Target Spot',
        'plant': 'Tomato',
        'severity': 'Moderate',
        'symptoms': 'Circular lesions with concentric rings (target pattern). Brown spots on leaves, stems, and fruit.',
        'prevention': 'Use resistant varieties. Proper plant spacing. Avoid leaf wetness.',
        'organic_treatment': 'Neem oil or copper fungicide spray at first sign.',
        'chemical_treatment': 'Fluxapyroxad or Azoxystrobin + Difenoconazole. Apply at disease onset.',
        'color': 'warning',
        'emoji': '🍅',
    },
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
        'display_name': 'Tomato Yellow Leaf Curl Virus (TYLCV)',
        'plant': 'Tomato',
        'severity': 'Critical',
        'symptoms': 'Severe leaf curling upwards, yellowing of leaf margins, stunted plant growth, reduced fruit setting. Caused by whitefly-transmitted virus.',
        'prevention': 'Use TYLCV-resistant varieties. Control whitefly populations with yellow sticky traps. Use insect-proof net-houses for nursery.',
        'organic_treatment': 'Spray neem oil + soap solution to control whitefly vectors. Remove and destroy infected plants.',
        'chemical_treatment': 'Imidacloprid 200 SL (0.5 ml/L) to control whitefly. No cure for the virus; infected plants must be uprooted.',
        'color': 'danger',
        'emoji': '🍅',
    },
    'Tomato___Tomato_mosaic_virus': {
        'display_name': 'Tomato Mosaic Virus (ToMV)',
        'plant': 'Tomato',
        'severity': 'High',
        'symptoms': 'Mosaic pattern of light and dark green areas on leaves. Leaf distortion, blistering, and stunted growth.',
        'prevention': 'Use virus-free certified seeds. Wash hands and disinfect tools before handling plants. Control aphids.',
        'organic_treatment': 'Remove and destroy infected plants. Control aphid and thrip vectors with neem spray.',
        'chemical_treatment': 'No chemical cure. Preventive: Mineral oil spray to reduce virus spread by aphids.',
        'color': 'danger',
        'emoji': '🍅',
    },
    'Tomato___Spider_mites_Two-spotted_spider_mite': {
        'display_name': 'Tomato Spider Mites',
        'plant': 'Tomato',
        'severity': 'Moderate',
        'symptoms': 'Fine webbing on leaf undersides. Tiny yellow speckling/stippling on upper leaf surface. Leaves become bronzed and dry in severe cases.',
        'prevention': 'Maintain adequate soil moisture. Avoid dusty conditions. Encourage natural predators.',
        'organic_treatment': 'Spray neem oil (5 ml/L) or insecticidal soap. Release predatory mites (Phytoseiulus persimilis).',
        'chemical_treatment': 'Abamectin 1.8 EC (0.5 ml/L) or Propargite 57 EC. Rotate miticides to prevent resistance.',
        'color': 'warning',
        'emoji': '🍅',
    },
    'Tomato___healthy': {
        'display_name': 'Healthy Tomato Plant',
        'plant': 'Tomato',
        'severity': 'None',
        'symptoms': 'No disease detected. Plant shows healthy green growth.',
        'prevention': 'Continue regular monitoring. Scout weekly for early pest or disease signs.',
        'organic_treatment': 'Monthly preventive neem oil spray is beneficial.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
    'Grape___Black_rot': {
        'display_name': 'Grape Black Rot',
        'plant': 'Grape',
        'severity': 'High',
        'symptoms': 'Circular tan spots with dark brown borders on leaves. Berries turn dark, shrivel into hard black mummies.',
        'prevention': 'Remove mummified berries and infected shoots. Ensure good canopy ventilation.',
        'organic_treatment': 'Sulfur-based fungicide or copper spray at bud burst.',
        'chemical_treatment': 'Myclobutanil or Mancozeb applied from bud burst through veraison at 10-14 day intervals.',
        'color': 'danger',
        'emoji': '🍇',
    },
    'Grape___Esca_(Black_Measles)': {
        'display_name': 'Grape Esca (Black Measles)',
        'plant': 'Grape',
        'severity': 'High',
        'symptoms': 'Tiger-stripe pattern on leaves. Berries develop dark spots and may shrivel. Internal wood shows dark streaking.',
        'prevention': 'Protect pruning wounds with fungicidal paste. Remove infected wood promptly.',
        'organic_treatment': 'Trichoderma-based wound protectants after pruning.',
        'chemical_treatment': 'Thiophanate-methyl paint on pruning wounds. No fully effective systemic treatment exists.',
        'color': 'danger',
        'emoji': '🍇',
    },
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': {
        'display_name': 'Grape Leaf Blight',
        'plant': 'Grape',
        'severity': 'Moderate',
        'symptoms': 'Irregular dark brown spots on leaves. Severely infected leaves turn yellow and drop.',
        'prevention': 'Good vineyard sanitation. Remove infected leaves and debris.',
        'organic_treatment': 'Copper fungicide spray. Bordeaux mixture application.',
        'chemical_treatment': 'Mancozeb 75 WP or Captan 50 WP at 10–14 day intervals.',
        'color': 'warning',
        'emoji': '🍇',
    },
    'Grape___healthy': {
        'display_name': 'Healthy Grape Vine',
        'plant': 'Grape',
        'severity': 'None',
        'symptoms': 'No disease detected. Vines show healthy green foliage.',
        'prevention': 'Regular dormant pruning. Maintain balanced nutrition.',
        'organic_treatment': 'Preventive sulfur dusting during humid periods.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
    'Orange___Haunglongbing_(Citrus_greening)': {
        'display_name': 'Citrus Greening (HLB)',
        'plant': 'Citrus / Orange',
        'severity': 'Critical',
        'symptoms': 'Asymmetric yellowing (blotchy mottle) of leaves. Stunted growth. Small, misshapen, bitter fruit with green coloring at base. Twig dieback.',
        'prevention': 'Use certified disease-free nursery plants. Control Asian citrus psyllid (the insect vector). Remove and destroy infected trees.',
        'organic_treatment': 'No cure exists. Aggressive psyllid control with neem oil sprays. Remove infected trees immediately to protect neighbors.',
        'chemical_treatment': 'Dimethoate or Imidacloprid for psyllid control. Infected trees must be removed — no systemic cure available.',
        'color': 'danger',
        'emoji': '🍊',
    },
    'Peach___Bacterial_spot': {
        'display_name': 'Peach Bacterial Spot',
        'plant': 'Peach',
        'severity': 'Moderate',
        'symptoms': 'Small, water-soaked angular spots on leaves turning purple-brown. Fruit shows sunken spots with rough texture.',
        'prevention': 'Plant resistant varieties. Avoid overhead irrigation. Prune for good air circulation.',
        'organic_treatment': 'Copper hydroxide spray. Avoid working in orchard when leaves are wet.',
        'chemical_treatment': 'Fixed copper sprays (Copper hydroxide 77 WP) applied from shuck split through harvest at 7–10 day intervals.',
        'color': 'warning',
        'emoji': '🍑',
    },
    'Peach___healthy': {
        'display_name': 'Healthy Peach Tree',
        'plant': 'Peach',
        'severity': 'None',
        'symptoms': 'No disease detected. Healthy green foliage observed.',
        'prevention': 'Annual dormant oil sprays. Regular fertilization. Monitor for peach leaf curl.',
        'organic_treatment': 'Preventive copper spray before bud swell.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
    'Pepper,_bell___Bacterial_spot': {
        'display_name': 'Bell Pepper Bacterial Spot',
        'plant': 'Bell Pepper',
        'severity': 'Moderate',
        'symptoms': 'Small, circular to irregular brown water-soaked spots on leaves and fruit. Spots may have yellow halos.',
        'prevention': 'Use certified seed. Practice 2–3 year crop rotation. Avoid overhead irrigation.',
        'organic_treatment': 'Copper-based bactericide spray. Remove infected plant parts.',
        'chemical_treatment': 'Copper hydroxide 77 WP (3 g/L) with Mancozeb. Spray at 7-day intervals during wet weather.',
        'color': 'warning',
        'emoji': '🫑',
    },
    'Pepper,_bell___healthy': {
        'display_name': 'Healthy Bell Pepper Plant',
        'plant': 'Bell Pepper',
        'severity': 'None',
        'symptoms': 'No disease detected. Plant is growing vigorously with green, unblemished leaves.',
        'prevention': 'Monitor for aphids and whitefly. Maintain consistent soil moisture.',
        'organic_treatment': 'Monthly neem oil spray as preventive measure.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
    'Cherry_(including_sour)___Powdery_mildew': {
        'display_name': 'Cherry Powdery Mildew',
        'plant': 'Cherry',
        'severity': 'Moderate',
        'symptoms': 'White powdery fungal coating on leaves, shoots, and fruit. Affected leaves curl and may drop.',
        'prevention': 'Plant in sunny locations with good air movement. Prune for open canopy structure.',
        'organic_treatment': 'Potassium bicarbonate or baking soda spray (1 tbsp/L). Sulfur dust applications.',
        'chemical_treatment': 'Myclobutanil, Tebuconazole, or Sulphur WP fungicide at petal fall and 2–3 weeks later.',
        'color': 'warning',
        'emoji': '🍒',
    },
    'Cherry_(including_sour)___healthy': {
        'display_name': 'Healthy Cherry Tree',
        'plant': 'Cherry',
        'severity': 'None',
        'symptoms': 'No disease detected. Healthy foliage and growth observed.',
        'prevention': 'Annual pruning for air circulation. Dormant copper spray before bud break.',
        'organic_treatment': 'Preventive sulfur spray in spring.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
    'Blueberry___healthy': {
        'display_name': 'Healthy Blueberry Plant',
        'plant': 'Blueberry',
        'severity': 'None',
        'symptoms': 'No disease detected. Healthy green foliage.',
        'prevention': 'Maintain acidic soil pH (4.5–5.5). Mulch heavily to conserve moisture.',
        'organic_treatment': 'Preventive neem oil spray monthly during season.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
    'Raspberry___healthy': {
        'display_name': 'Healthy Raspberry Plant',
        'plant': 'Raspberry',
        'severity': 'None',
        'symptoms': 'No disease detected.',
        'prevention': 'Prune old canes after fruiting. Ensure good drainage.',
        'organic_treatment': 'Preventive copper spray before new growth in spring.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
    'Soybean___healthy': {
        'display_name': 'Healthy Soybean Plant',
        'plant': 'Soybean',
        'severity': 'None',
        'symptoms': 'No disease detected. Plants showing normal vigorous growth.',
        'prevention': 'Crop rotation. Balanced fertilization. Scout regularly for Asian soybean rust.',
        'organic_treatment': 'Trichoderma soil application. Preventive neem spray.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
    'Squash___Powdery_mildew': {
        'display_name': 'Squash Powdery Mildew',
        'plant': 'Squash',
        'severity': 'Moderate',
        'symptoms': 'White powdery spots on upper and lower leaf surfaces. Affected leaves turn yellow and dry out.',
        'prevention': 'Plant resistant varieties. Avoid overhead watering. Good plant spacing for air circulation.',
        'organic_treatment': 'Spray diluted neem oil (5 ml/L) or baking soda solution (1 tsp/L water). Remove infected leaves.',
        'chemical_treatment': 'Sulphur 80 WP (3 g/L) or Myclobutanil at first sign of disease. Repeat every 10 days.',
        'color': 'warning',
        'emoji': '🎃',
    },
    'Strawberry___Leaf_scorch': {
        'display_name': 'Strawberry Leaf Scorch',
        'plant': 'Strawberry',
        'severity': 'Moderate',
        'symptoms': 'Small, purple to red spots on upper leaf surface. Centers may turn tan/gray. Severely infected leaves look "scorched".',
        'prevention': 'Plant resistant varieties. Avoid overhead irrigation. Remove old infected leaves at renovation.',
        'organic_treatment': 'Copper-based fungicide spray. Remove and destroy severely infected leaves.',
        'chemical_treatment': 'Myclobutanil, Captan, or Iprodione fungicide. Apply at first sign of symptoms.',
        'color': 'warning',
        'emoji': '🍓',
    },
    'Strawberry___healthy': {
        'display_name': 'Healthy Strawberry Plant',
        'plant': 'Strawberry',
        'severity': 'None',
        'symptoms': 'No disease detected. Leaves are healthy and green.',
        'prevention': 'Maintain good air circulation. Avoid planting in areas with history of soil-borne diseases.',
        'organic_treatment': 'Monthly neem oil preventive spray.',
        'chemical_treatment': 'No treatment required.',
        'color': 'success',
        'emoji': '✅',
    },
}

# Default fallback for any class not in DISEASE_KNOWLEDGE
DEFAULT_INFO = {
    'display_name': 'Unknown Condition',
    'plant': 'Unknown',
    'severity': 'Unknown',
    'symptoms': 'Please consult a local agricultural extension officer for accurate diagnosis.',
    'prevention': 'Maintain good crop hygiene and scout fields regularly.',
    'organic_treatment': 'Consult your local Krishi Vigyan Kendra (KVK) for organic treatment options.',
    'chemical_treatment': 'Consult a certified agrochemical dealer for appropriate treatment.',
    'color': 'secondary',
    'emoji': '🌿',
}


# ─────────────────────────────────────────────
# Model predictor class
# ─────────────────────────────────────────────

class PlantDiseasePredictor:
    """
    Wraps MobileNetV2 (trained on PlantVillage, 38 classes) for inference.
    Falls back to Demo Simulation Mode if PyTorch/model weights are unavailable.
    """

    MODEL_WEIGHTS_PATH = Path(__file__).parent / 'weights' / 'plant_disease_mobilenetv2.pth'
    # Hugging Face direct download for the .pth weights file
    WEIGHTS_URL = 'https://huggingface.co/linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification/resolve/main/model.pth'

    _instance = None   # Singleton

    def __init__(self):
        self.model = None
        self.transform = None
        self.mode = 'demo'   # 'ai' or 'demo'
        self._load_model()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ── private helpers ──────────────────────────────────────

    def _load_model(self):
        """Try to load PyTorch model; fall back gracefully on any error."""
        try:
            import torch
            import torchvision.transforms as transforms
            from torchvision.models import mobilenet_v2

            # Build model architecture
            model = mobilenet_v2(weights=None)
            # Modify classifier head for 38 plant disease classes
            import torch.nn as nn
            model.classifier[1] = nn.Linear(model.last_channel, len(PLANT_DISEASE_CLASSES))

            weights_path = self.MODEL_WEIGHTS_PATH

            if not weights_path.exists():
                logger.info("PlantDoctor: weights not found locally — attempting download …")
                self._download_weights(weights_path)

            if weights_path.exists():
                state = torch.load(str(weights_path), map_location='cpu', weights_only=True)
                # Support both raw state_dict and checkpoint dicts
                if isinstance(state, dict) and 'model_state_dict' in state:
                    state = state['model_state_dict']
                elif isinstance(state, dict) and 'state_dict' in state:
                    state = state['state_dict']
                model.load_state_dict(state, strict=False)
                model.eval()
                self.model = model

                self.transform = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225]
                    ),
                ])
                self.mode = 'ai'
                logger.info("PlantDoctor: AI model loaded successfully ✓")
            else:
                logger.warning("PlantDoctor: weight download failed — using Demo Simulation Mode")
                self.mode = 'demo'

        except ImportError:
            logger.warning("PlantDoctor: PyTorch not installed — using Demo Simulation Mode")
            self.mode = 'demo'
        except Exception as exc:
            logger.warning(f"PlantDoctor: model load error ({exc}) — using Demo Simulation Mode")
            self.mode = 'demo'

    def _download_weights(self, dest: Path):
        """Download model weights from Hugging Face."""
        try:
            import requests
            dest.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Downloading model weights to {dest} …")
            resp = requests.get(self.WEIGHTS_URL, timeout=120, stream=True)
            if resp.status_code == 200:
                with open(dest, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info("PlantDoctor: weights downloaded successfully ✓")
            else:
                logger.warning(f"PlantDoctor: download returned HTTP {resp.status_code}")
        except Exception as exc:
            logger.warning(f"PlantDoctor: download exception — {exc}")

    # ── public inference method ───────────────────────────────

    def predict(self, image_bytes: bytes) -> dict:
        """
        Run disease prediction on raw image bytes.
        Returns a dict with keys: mode, predictions (list of top-3), primary.
        """
        if self.mode == 'ai':
            return self._predict_ai(image_bytes)
        else:
            return self._predict_demo(image_bytes)

    def _predict_ai(self, image_bytes: bytes) -> dict:
        """Real PyTorch inference."""
        try:
            import torch
            import torch.nn.functional as F
            from PIL import Image

            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            tensor = self.transform(img).unsqueeze(0)

            with torch.no_grad():
                logits = self.model(tensor)
                probs = F.softmax(logits, dim=1)[0]

            top3_probs, top3_idx = torch.topk(probs, 3)
            predictions = []
            for prob, idx in zip(top3_probs.tolist(), top3_idx.tolist()):
                class_key = PLANT_DISEASE_CLASSES[idx]
                info = DISEASE_KNOWLEDGE.get(class_key, DEFAULT_INFO).copy()
                info['class_key'] = class_key
                info['confidence'] = round(prob * 100, 1)
                predictions.append(info)

            return {
                'mode': 'ai',
                'predictions': predictions,
                'primary': predictions[0],
            }
        except Exception as exc:
            logger.error(f"PlantDoctor AI inference error: {exc}")
            return self._predict_demo(image_bytes)  # Graceful fallback

    def _predict_demo(self, image_bytes: bytes) -> dict:
        """
        Demo Simulation Mode.
        Uses a deterministic hash of the image bytes to pick a consistent
        disease class so repeated uploads of the same image give the same result.
        Skips purely 'healthy' classes to make demos more interesting.
        """
        # Use image hash for determinism
        digest = int(hashlib.md5(image_bytes).hexdigest(), 16)

        # Pick from disease classes (exclude healthy for better demo)
        disease_classes = [c for c in PLANT_DISEASE_CLASSES if 'healthy' not in c]
        primary_key = disease_classes[digest % len(disease_classes)]

        # Build top-3 picks
        random.seed(digest)
        other_keys = [c for c in disease_classes if c != primary_key]
        random.shuffle(other_keys)
        top3_keys = [primary_key] + other_keys[:2]

        # Simulate realistic confidence scores
        confs = sorted([random.uniform(55, 92), random.uniform(5, 20), random.uniform(2, 10)], reverse=True)

        predictions = []
        for key, conf in zip(top3_keys, confs):
            info = DISEASE_KNOWLEDGE.get(key, DEFAULT_INFO).copy()
            info['class_key'] = key
            info['confidence'] = round(conf, 1)
            predictions.append(info)

        return {
            'mode': 'demo',
            'predictions': predictions,
            'primary': predictions[0],
        }


# ── Module-level convenience function ────────────────────────

def get_predictor() -> PlantDiseasePredictor:
    return PlantDiseasePredictor.get_instance()
