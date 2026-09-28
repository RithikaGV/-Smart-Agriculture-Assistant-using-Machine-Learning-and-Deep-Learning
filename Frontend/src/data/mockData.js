export const DEFAULT_PLANT_IMAGE = "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=800&q=80";

export const INITIAL_PLANTS = [
  {
    id: "plant-1",
    name: "Hydroponic Roma Tomato",
    species: "Tomato (Solanum lycopersicum)",
    location: "Greenhouse Alpha - Bay 1",
    image: "https://images.unsplash.com/photo-1592841200221-a6898f307baa?auto=format&fit=crop&w=800&q=80",
    status: "Healthy", // Healthy, Good, Needs Attention, Critical
    metrics: {
      temperature: 24.2, // °C
      ph: 6.3,
      humidity: 68, // %
      waterLevel: 85, // %
    },
    sensors: {
      temperature: { connected: true, battery: 92, address: "BLE-TEMP-089A", statusText: "Connected and battery level good" },
      ph: { connected: true, battery: 88, address: "I2C-PH-401X", statusText: "Connected and battery level good" },
      waterLevel: { connected: true, battery: 15, address: "ADC-WTR-202B", statusText: "Connected battery low" },
      humidity: { connected: true, battery: 94, address: "BLE-HUM-011C", statusText: "Connected and battery level good" }
    },
    growthHistory: [
      { day: "Day 1", heightCm: 12, ph: 6.1, temp: 23.5, humidity: 65, water: 95 },
      { day: "Day 5", heightCm: 18, ph: 6.2, temp: 24.0, humidity: 66, water: 90 },
      { day: "Day 10", heightCm: 25, ph: 6.3, temp: 24.2, humidity: 68, water: 85 },
      { day: "Day 15", heightCm: 32, ph: 6.3, temp: 24.1, humidity: 67, water: 82 },
      { day: "Day 20", heightCm: 41, ph: 6.4, temp: 24.5, humidity: 70, water: 78 }
    ],
    notes: "Optimal nutrient intake. High fruit yield anticipated."
  },
  {
    id: "plant-2",
    name: "Red Bell Pepper Batch",
    species: "Bell Pepper (Capsicum annuum)",
    location: "Greenhouse Alpha - Bay 3",
    image: "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?auto=format&fit=crop&w=800&q=80",
    status: "Needs Attention",
    metrics: {
      temperature: 31.8, // Slightly high
      ph: 5.1, // Acidic
      humidity: 78,
      waterLevel: 32,
    },
    sensors: {
      temperature: { connected: true, battery: 74, address: "BLE-TEMP-112B", statusText: "Connected and battery level good" },
      ph: { connected: true, battery: 65, address: "I2C-PH-109Z", statusText: "Connected and battery level good" },
      waterLevel: { connected: false, battery: 0, address: "ADC-WTR-999X", statusText: "Not Connected" },
      humidity: { connected: true, battery: 81, address: "BLE-HUM-304D", statusText: "Connected and battery level good" }
    },
    growthHistory: [
      { day: "Day 1", heightCm: 10, ph: 5.8, temp: 26.0, humidity: 70, water: 80 },
      { day: "Day 5", heightCm: 15, ph: 5.5, temp: 28.5, humidity: 72, water: 65 },
      { day: "Day 10", heightCm: 21, ph: 5.3, temp: 30.1, humidity: 75, water: 45 },
      { day: "Day 15", heightCm: 26, ph: 5.1, temp: 31.8, humidity: 78, water: 32 }
    ],
    notes: "Temperature rising. Water level sensor disconnected. Requires pH adjustment."
  },
  {
    id: "plant-3",
    name: "Crisp Butterhead Lettuce",
    species: "Lettuce (Lactuca sativa)",
    location: "Vertical Farm Tower B",
    image: "https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?auto=format&fit=crop&w=800&q=80",
    status: "Healthy",
    metrics: {
      temperature: 21.5,
      ph: 6.0,
      humidity: 62,
      waterLevel: 94,
    },
    sensors: {
      temperature: { connected: true, battery: 96, address: "BLE-TEMP-887K", statusText: "Connected and battery level good" },
      ph: { connected: true, battery: 91, address: "I2C-PH-554M", statusText: "Connected and battery level good" },
      waterLevel: { connected: true, battery: 89, address: "ADC-WTR-331L", statusText: "Connected and battery level good" },
      humidity: { connected: true, battery: 93, address: "BLE-HUM-220P", statusText: "Connected and battery level good" }
    },
    growthHistory: [
      { day: "Day 1", heightCm: 5, ph: 6.0, temp: 21.0, humidity: 60, water: 98 },
      { day: "Day 5", heightCm: 11, ph: 6.0, temp: 21.2, humidity: 61, water: 96 },
      { day: "Day 10", heightCm: 17, ph: 6.0, temp: 21.5, humidity: 62, water: 94 }
    ],
    notes: "Exemplary growth under LED spectrum lights."
  },
  {
    id: "plant-4",
    name: "Sweet Alpine Strawberries",
    species: "Strawberry (Fragaria vesca)",
    location: "Hydroponic Bench 4",
    image: "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=800&q=80",
    status: "Critical",
    metrics: {
      temperature: 34.5, // High alert
      ph: 4.8, // Very acidic
      humidity: 89, // Mold risk
      waterLevel: 12, // Critical low
    },
    sensors: {
      temperature: { connected: true, battery: 12, address: "BLE-TEMP-998Q", statusText: "Connected battery low" },
      ph: { connected: true, battery: 45, address: "I2C-PH-887R", statusText: "Connected and battery level good" },
      waterLevel: { connected: true, battery: 8, address: "ADC-WTR-114S", statusText: "Connected battery low" },
      humidity: { connected: false, battery: 0, address: "BLE-HUM-0000", statusText: "Not Connected" }
    },
    growthHistory: [
      { day: "Day 1", heightCm: 8, ph: 5.6, temp: 24.0, humidity: 65, water: 90 },
      { day: "Day 5", heightCm: 12, ph: 5.2, temp: 29.0, humidity: 75, water: 50 },
      { day: "Day 10", heightCm: 14, ph: 4.8, temp: 34.5, humidity: 89, water: 12 }
    ],
    notes: "CRITICAL: Urgent intervention needed. Reservoir dry & high temperature!"
  },
  {
    id: "plant-5",
    name: "Golden Sweet Corn",
    species: "Corn (Zea mays)",
    location: "Outdoor Smart Bed 2",
    image: "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=800&q=80",
    status: "Good",
    metrics: {
      temperature: 26.8,
      ph: 6.6,
      humidity: 58,
      waterLevel: 72,
    },
    sensors: {
      temperature: { connected: true, battery: 85, address: "BLE-TEMP-303C", statusText: "Connected and battery level good" },
      ph: { connected: true, battery: 80, address: "I2C-PH-707D", statusText: "Connected and battery level good" },
      waterLevel: { connected: true, battery: 77, address: "ADC-WTR-505E", statusText: "Connected and battery level good" },
      humidity: { connected: true, battery: 84, address: "BLE-HUM-404F", statusText: "Connected and battery level good" }
    },
    growthHistory: [
      { day: "Day 1", heightCm: 15, ph: 6.5, temp: 25.0, humidity: 60, water: 85 },
      { day: "Day 5", heightCm: 30, ph: 6.6, temp: 26.0, humidity: 59, water: 78 },
      { day: "Day 10", heightCm: 48, ph: 6.6, temp: 26.8, humidity: 58, water: 72 }
    ],
    notes: "Strong stem development."
  }
];

export const INITIAL_ALERTS = [
  {
    id: "alert-1",
    plantId: "plant-4",
    plantName: "Sweet Alpine Strawberries",
    severity: "critical", // critical, warning, info
    type: "Temperature & Water Level",
    title: "High Temperature & Critical Water Level",
    description: "Temperature has reached 34.5°C (Threshold: <28°C) and water level dropped to 12% (Threshold: >30%). High risk of heat shock.",
    remedyText: "Turn on the evaporative cooling fan and trigger automated pump refill to top up water reservoir immediately.",
    remedyAction: "COOLING_AND_REFILL",
    timestamp: "10 minutes ago"
  },
  {
    id: "alert-2",
    plantId: "plant-2",
    plantName: "Red Bell Pepper Batch",
    severity: "warning",
    type: "pH Acidic Level",
    title: "Water Acidic (pH 5.1)",
    description: "pH has dropped to 5.1 (Ideal Range: 5.8 - 6.5). Nutrient absorption is impaired.",
    remedyText: "Add 15ml of Alkali Buffer (pH Up solution) to balance acidity back to ~6.2.",
    remedyAction: "ADD_ALKALI",
    timestamp: "35 minutes ago"
  },
  {
    id: "alert-3",
    plantId: "plant-4",
    plantName: "Sweet Alpine Strawberries",
    severity: "warning",
    type: "Humidity & Mold Risk",
    title: "High Air Humidity (89%)",
    description: "Excessive relative air humidity increases risks of foliar fungal pathogens and gray mold (Botrytis).",
    remedyText: "Activate air circulation de-humidifiers and open automated ventilation louvers.",
    remedyAction: "ACTIVATE_DEHUMIDIFIER",
    timestamp: "1 hour ago"
  },
  {
    id: "alert-4",
    plantId: "plant-2",
    plantName: "Red Bell Pepper Batch",
    severity: "info",
    type: "Sensor Disconnected",
    title: "Water Level Sensor Disconnected",
    description: "Telemetry offline for address ADC-WTR-999X.",
    remedyText: "Check physical sensor cable wiring or reconnect sensor module via My Plants setup.",
    remedyAction: "RECONNECT_SENSOR",
    timestamp: "2 hours ago"
  }
];

export const SAMPLE_DISEASE_DATASET = [
  {
    id: "sample-1",
    name: "Tomato Early Blight",
    scientificName: "Alternaria solani",
    confidence: 97.8,
    plantType: "Tomato",
    image: "https://images.unsplash.com/photo-1592841200221-a6898f307baa?auto=format&fit=crop&w=800&q=80",
    cause: "Caused by the fungal pathogen Alternaria solani. Thrives in warm temperatures (24-29°C) accompanied by high humidity, prolonged leaf wetness, or heavy dew.",
    preventiveMeasures: [
      "Apply copper-based or chlorothalonil fungicide sprays at 7-10 day intervals.",
      "Prune and remove infected lower leaves to restrict fungal spore splash.",
      "Ensure proper plant spacing and drip irrigation so foliage remains dry.",
      "Rotate crops with non-solanaceous plants next season."
    ]
  },
  {
    id: "sample-2",
    name: "Corn Common Rust",
    scientificName: "Puccinia sorghi",
    confidence: 95.4,
    plantType: "Corn",
    image: "https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=800&q=80",
    cause: "Caused by the fungus Puccinia sorghi. Spores are windborne and infect leaf tissue during cool, moist nights (16-23°C) with high relative humidity (>90%).",
    preventiveMeasures: [
      "Plant resistant hybrid corn seed varieties.",
      "Apply triazole or strobilurin fungicides if disease spreads to upper canopy prior to flowering.",
      "Avoid overhead sprinkler irrigation during humid evening periods."
    ]
  },
  {
    id: "sample-3",
    name: "Apple Black Rot",
    scientificName: "Botryosphaeria obtusa",
    confidence: 98.2,
    plantType: "Apple Tree",
    image: "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=800&q=80",
    cause: "Fungal infection overwintering in mummified fruit, dead wood, and bark cankers. Favored by rainy warm periods post-blossom.",
    preventiveMeasures: [
      "Prune out dead branches, diseased twigs, and remove any mummified apples from trees.",
      "Apply captan or sulfur-based organic sprays during early leaf unfolding.",
      "Keep orchard floor clear of fallen leaf litter and debris."
    ]
  },
  {
    id: "sample-4",
    name: "Healthy Organic Leaf",
    scientificName: "N/A - Non-Pathogenic",
    confidence: 99.4,
    plantType: "Pepper / Tomato / Mixed",
    image: "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?auto=format&fit=crop&w=800&q=80",
    cause: "No pathogen or metabolic lesion detected. Stomata and chlorophyll structure are in prime condition.",
    preventiveMeasures: [
      "Maintain existing optimal fertigation schedules.",
      "Continue monitoring water pH between 5.8 and 6.5.",
      "Inspect leaves weekly for early pest detection."
    ]
  }
];

export const INITIAL_GROWER_PROFILE = {
  name: "Dr. Rajesh Kumar",
  email: "rajesh.kumar@smartagri.org",
  address: "Plot 42, Agritech Innovation Hub, Sector 18",
  state: "Karnataka",
  country: "India",
  pincode: "560100",
  memberSince: "2024",
  farmType: "Smart Hydroponics & IoT Greenhouse"
};
