import json
import os
from sqlalchemy.orm import Session
from app.models.domain import Grower, Farm, HydroponicSystem, Plant, Sensor, Alert

EXPORT_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data_export.json")
EXPORT_MD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data_export.md")

def export_readable_data(db: Session):
    try:
        growers = db.query(Grower).all()
        farms = db.query(Farm).all()
        systems = db.query(HydroponicSystem).all()
        plants = db.query(Plant).all()
        alerts = db.query(Alert).filter(Alert.resolved == False).all()

        export_data = {
            "summary": {
                "total_growers": len(growers),
                "total_farms": len(farms),
                "total_systems": len(systems),
                "total_plants": len(plants),
                "active_alerts": len(alerts)
            },
            "growers": [],
            "plants": [],
            "active_alerts": []
        }

        grower_map = {g.id: g.email for g in growers}

        for g in growers:
            grower_farms = [f for f in farms if f.grower_id == g.id]
            grower_plants = [p for p in plants if p.grower_id == g.id]
            export_data["growers"].append({
                "id": g.id,
                "name": g.name,
                "email": g.email,
                "address": g.address,
                "farm_type": g.farm_type,
                "total_farms": len(grower_farms),
                "total_plants": len(grower_plants)
            })

        for p in plants:
            sensors = db.query(Sensor).filter(Sensor.plant_id == p.id).all()
            sensor_list = [
                {
                    "type": s.sensor_type,
                    "address": s.address,
                    "connected": s.connected,
                    "battery": f"{s.battery}%"
                }
                for s in sensors
            ]

            export_data["plants"].append({
                "id": p.id,
                "grower_id": p.grower_id,
                "grower_email": grower_map.get(p.grower_id, "unknown"),
                "system_id": p.system_id,
                "name": p.name,
                "species": p.species,
                "location": p.location,
                "status": p.status,
                "metrics": {
                    "temperature": f"{p.temperature}°C",
                    "ph": f"pH {p.ph}",
                    "humidity": f"{p.humidity}%",
                    "water_level": f"{p.water_level}%"
                },
                "sensors": sensor_list,
                "notes": p.notes
            })

        for a in alerts:
            export_data["active_alerts"].append({
                "id": a.id,
                "grower_id": a.grower_id,
                "plant_id": a.plant_id,
                "severity": a.severity,
                "title": a.title,
                "description": a.description,
                "remedy": a.remedy_text,
                "timestamp": a.timestamp
            })

        # Save JSON File (pretty formatted with grower_id explicitly shown)
        with open(EXPORT_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        # Save Markdown File grouped by Grower
        md_lines = ["# Hydroponics Assistant - Multi-Tenant Data Export\n"]
        md_lines.append(f"**Total Growers:** {len(growers)} | **Total Plants:** {len(plants)} | **Active Alerts:** {len(alerts)}\n")
        
        for g in growers:
            g_plants = [p for p in export_data["plants"] if p["grower_id"] == g.id]
            md_lines.append(f"## 👤 Grower: {g.name} (`{g.id}` - {g.email})\n")
            if not g_plants:
                md_lines.append("_No plants registered for this grower yet._\n")
            else:
                for p in g_plants:
                    md_lines.append(f"### 🌿 {p['name']} (`{p['id']}`)")
                    md_lines.append(f"- **Grower ID:** `{p['grower_id']}` ({p['grower_email']})")
                    md_lines.append(f"- **Species:** {p['species']}")
                    md_lines.append(f"- **Location:** {p['location']}")
                    md_lines.append(f"- **Status:** `{p['status']}`")
                    md_lines.append(f"- **Metrics:** Temp: {p['metrics']['temperature']} | pH: {p['metrics']['ph']} | Humidity: {p['metrics']['humidity']} | Water Level: {p['metrics']['water_level']}")
                    md_lines.append(f"- **Notes:** {p['notes'] or 'N/A'}")
                    md_lines.append("- **Connected Sensors:**")
                    for s in p["sensors"]:
                        status_icon = "🟢" if s['connected'] else "🔴"
                        md_lines.append(f"  - {status_icon} `{s['type']}` (Address: `{s['address']}`, Battery: {s['battery']})")
                    md_lines.append("")

        if export_data["active_alerts"]:
            md_lines.append("## ⚠️ Active Alerts\n")
            for a in export_data["active_alerts"]:
                md_lines.append(f"- **[{a['severity'].upper()}] {a['title']}** (Grower ID: `{a['grower_id']}`, Plant: `{a['plant_id']}`) - {a['description']}")
                md_lines.append(f"  - *Remedy:* {a['remedy']}\n")

        with open(EXPORT_MD_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return EXPORT_JSON_PATH
    except Exception as e:
        print(f"Exporter error: {e}")
        return None
