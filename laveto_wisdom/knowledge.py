"""
laveto_wisdom/knowledge.py
Comprehensive Statutory Ground-Truth Reference Knowledge Engine for Botswana.
Covers 10 Sectoral Frameworks, 8 SEZA Clusters, P9.2B Macro Deficit Data, and IRP Baselines.
"""

BOTSWANA_GROUND_TRUTH = """
[BOTSWANA STATUTORY BENCHMARKS & STRATEGIC MARKET INTELLIGENCE]

1. SEZA GEOGRAPHIC HUBS & PRIORITY INVESTMENT MANDATES:
- General Statutory Threshold: Minimum BWP 50 Million (P50M) capital investment with verified export orientation or proven domestic import substitution derogation.
- The 8 Dedicated SEZA Industrial Clusters:
  * 1. Pandamatenga (Agro-Processing & Grain Storage): Commercial grain production, bulk silo warehousing, water reticulation, and oilseed solvent extraction/crushing.
  * 2. Lobatse (Meat Beneficiation & Leather Park): Beef and small-stock processing, national leather tannery park, dairy processing, and biopharmaceuticals.
  * 3. Selebi-Phikwe / SPEDU (Metallurgy & Circular Industry): Heavy engineering, metal fabrication, copper/nickel slag recovery, textile recycling, clean metallurgy.
  * 4. Sir Seretse Khama International Airport / SSKIA (High-Value Cargo & Diamonds): Diamond cutting, polishing, and jewelry design (ODC quotas); aviation maintenance; perishable cargo cold-chain logistics.
  * 5. Fairgrounds (Financial & Business Services): International financial services centre (IFSC), fintech, legal tech, enterprise data warehousing, and venture capital.
  * 6. Francistown (Mining Supply Logistics & Multi-Modal Hub): Multi-modal freight transfer connecting SADC rail/road networks; mining equipment assembly, maintenance, and heavy haulage services.
  * 7. Palapye (Energy & Clean Coal Technologies): Coal-bed methane (CBM) extraction, synthetic fuels, clean coal engineering, and solar PV integration into national transmission.
  * 8. Tuli Block (Horticulture & Controlled Agriculture): High-efficiency precision horticulture, citrus packing, protected cold storage, and drip-irrigated citrus/vegetable clusters.

2. SPEDU SPECIAL INCENTIVE DEROGATIONS (SELEBI-PHIKWE):
- Fiscal Framework: Preferential 5% corporate tax rate for the first 5 years (10% thereafter).
- Customs Relief: Zero customs duty on imported industrial raw materials, capital equipment, and tooling.
- Land Tenure: Long-term statutory industrial land leasehold up to 50 years with subsidized ground rentals.

3. CITIZEN ECONOMIC EMPOWERMENT (CEE) & 35 PROTECTED SECTORS:
- Mandatory 50% Subcontracting: Public Procurement Act (2022) mandates a minimum 50% citizen subcontracting allocation on all major infrastructure and state-backed projects.
- Citizen Equity Reserves: 35 statutory sectors reserved exclusively for 100% citizen-owned micro and medium enterprises (school feeding, haulage, borehole maintenance, security, routine civil works, transport).
- Price Preferences: 8% to 15% price preference margins for citizen bidders in state tenders.

4. CRITICAL MINERAL BENEFICIATION & EXPORT RESTRICTIONS:
- Diamonds: Minerals Development framework mandates fulfillment of domestic supply quotas (15% to 25% rough stone allocation to local cutting and polishing factories before rough export).
- Battery Metals & Copper/Nickel: Complete prohibition on exporting raw, uncrushed copper, nickel, or lithium ores without secondary smelting, solvent extraction, or domestic processing.

5. AGRO-PROCESSING, DAIRY DEFICITS & COLD-CHAIN REALITIES:
- National Food Import Bill: Exceeds P9.2 Billion annually (~21.7% of all imports; NDP 12 target enforces reduction to 13.7% by 2030).
- Dairy Yield Deficit: Domestic production fulfills only 12% of the national demand of 65 million liters/year. The structural deficit is raw milk; processing facilities that bypass dairy farming or lack verified fodder hedges face imminent insolvency.
- Horticultural Spoilage: Seasonal import bans protect local growers, but lack of decentralized packhouses and cold storage causes 35% to 40% post-harvest loss during harvest gluts.
- Oilseed Processing: Complete deficit in domestic solvent extraction forces Pandamatenga sunflower crops to be exported raw to South Africa, losing domestic livestock feed cake.

6. ENERGY UNBUNDLING & IRP RENEWABLE TARGETS:
- Solar Resource & Targets: >3,200 peak sunshine hours; Integrated Resource Plan (IRP) mandates >30% renewable grid contribution by 2030.
- Power Reform: BPC unbundling enables private IPPs to connect under BERA grid code and export power via the Southern African Power Pool (SAPP).
- Clean Tech Relief: Zero-rated VAT on solar panels, inverters, and battery storage hardware.

7. WATER SCARCITY & CLOSED-LOOP RECLAMATION:
- Aridity Baseline: Over 70% of Botswana is semi-arid Kalahari. Groundwater depletion is an existential tail-risk.
- Industrial Regulations: High water-consuming operations (wet cooling, tanneries, feedlots) face severe WUC penal abstraction tariffs and mandatory closed-loop greywater treatment.
"""

STATUTORY_FRAMEWORKS = {
    "MINING_BENEFICIATION": {
        "acts": [
            "Mines and Minerals Act [Cap 66:01], Sections 4 & 11",
            "Minerals Development Framework (MDF)",
            "Diamond Cutting Act [Cap 66:04]",
            "Precious and Semi-Precious Stones (Protection) Act"
        ],
        "mandatory_covenants": [
            "Prohibition on raw, run-of-mine uncrushed ore exports without formal ministerial waiver.",
            "Mandatory on-site secondary/tertiary beneficiation or hydrometallurgical refining.",
            "Diamond cutting licensees must service domestic cutting factories and citizen skills transfer.",
            "Minimum 50% citizen subcontracting across logistics, haulage, and site services (Public Procurement Act 2022)."
        ],
        "triggers": ["mining", "ore", "lithium", "manganese", "copper", "diamond", "smelting", "beneficiation", "quarry"]
    },
    "SEZA_AND_SPEDU": {
        "acts": [
            "Special Economic Zones Act (No. 23 of 2015)",
            "SPEDU Special Economic Incentives Framework",
            "Economic Inclusion Act 2021"
        ],
        "clusters": {
            "SSKIA": "Aero-Cargo, Diamond Value-Addition, High-Tech Aviation Logistics",
            "SPEDU_SELEBI_PHIKWE": "Clean Metallurgy, Heavy Engineering, Circular Economy, Agro-Industrial",
            "FAIRGROUNDS": "Financial Services, IFSC, FinTech, International Arbitration",
            "LOBATSE": "Meat & Leather Processing Park, Bio-Chemicals",
            "PALAPYE": "Energy Derivatives, Coal-to-Chemicals, Captive Power",
            "PANDAMATENGA": "Commercial Grain Production, Silo Storage, Agro-Food Processing",
            "TULI_BLOCK": "Precision Horticulture, Citrus Packing, Cold Storage",
            "FRANCISTOWN": "Mining Supply Logistics, Freight Hub"
        },
        "fiscal_rules": [
            "Concessionary corporate tax: 5% for first 10 years, 10% thereafter.",
            "Zero customs duty on imported capital equipment, tooling, and clean plant tech.",
            "Fast-tracked sub-leases and expatriate quotas tied to citizen skills transfer agreements."
        ],
        "triggers": ["seza", "spedu", "zone", "cluster", "tax incentive", "concessionary", "industrial park"]
    },
    "WATER_AND_AGRICULTURE": {
        "acts": [
            "Water Act [Cap 34:01]",
            "National Water Policy & Department of Water Affairs Guidelines",
            "Botswana Agricultural Marketing Board (BAMB) Act [Cap 74:06]",
            "National Development Plan (NDP 12) Food Security Mandate"
        ],
        "mandatory_covenants": [
            "Industrial borehole abstraction permits require certified water-recycling circuit breakers.",
            "Minimum 80% closed-loop effluent recycling for hydrometallurgical plants, chemical units, and tanneries.",
            "Pandamatenga/Chobe agro-investors must reserve 30% strategic grain/pulse reserve off-take for BAMB.",
            "Strict non-degradation buffer zones around the Okavango Delta, Makgadikgadi Pans, and Limpopo basin."
        ],
        "triggers": ["water", "aquifer", "agriculture", "grain", "farming", "effluent", "irrigation", "leather", "bamb"]
    },
    "ENERGY_AND_IPP": {
        "acts": [
            "Botswana Energy Regulatory Authority (BERA) Act 2016",
            "Integrated Resource Plan (IRP 2020-2040)",
            "Botswana Power Corporation (BPC) Grid Code & Wheeling Framework"
        ],
        "mandatory_covenants": [
            "Industrial baseload demands >10 MW must integrate captive renewable capacity (Solar PV/BESS).",
            "BERA IPP licenses require grid stability proof and standard bankable PPA adherence.",
            "Grid-tied interconnections must grant non-discriminatory third-party open access wheeling."
        ],
        "triggers": ["energy", "solar", "ipp", "grid", "power", "bpc", "bera", "transmission", "bess", "megawatt"]
    },
    "DATA_AND_CYBER_SOVEREIGNTY": {
        "acts": [
            "Data Protection Act (DPA) 2018 / 2021",
            "Cybercrime and Computer Related Crimes Act",
            "National Spatial Data Infrastructure (NSDI) Policy"
        ],
        "mandatory_covenants": [
            "Geological datasets, mineral telemetry, and citizen biometric data must reside in domestic Tier-3 data centers.",
            "Cross-border transfer of industrial SCADA control feeds prohibited without regulatory waiver.",
            "Sovereign audit and code-inspection rights over automated industrial systems."
        ],
        "triggers": ["data", "telemetry", "cloud", "server", "scada", "cyber", "ai", "hosting", "software"]
    }
}

def get_ground_truth_context(proposal_text: str = "") -> str:
    """Returns the empirical Botswana ground-truth corpus for decision audits."""
    return BOTSWANA_GROUND_TRUTH.strip()

def retrieve_statutory_context(text: str = "") -> str:
    """Matches proposal text against statutory frameworks and compiles legal ground-truth."""
    matched = []
    t_lower = text.lower() if text else ""
    
    # Cross-cutting baselines
    matched.append(
        "### [CROSS-CUTTING MANDATE] CITIZEN ECONOMIC EMPOWERMENT:\n"
        "- Legislation: Economic Inclusion Act 2021, Public Procurement Act 2022\n"
        "- Mandate: 50% citizen subcontracting and local content ring-fencing are non-negotiable."
    )
    matched.append(
        "### [CROSS-CUTTING MANDATE] DATA & TELEMETRY SOVEREIGNTY:\n"
        "- Legislation: Data Protection Act (DPA) 2018 / 2021\n"
        "- Mandate: Domestic Tier-3 data hosting for operational, geospatial, and employee records."
    )

    for domain, data in STATUTORY_FRAMEWORKS.items():
        if domain in ["DATA_AND_CYBER_SOVEREIGNTY"]:
            continue
            
        triggers = data.get("triggers", [])
        is_matched = any(trig in t_lower for trig in triggers) if t_lower else True
        
        if is_matched or domain in ["MINING_BENEFICIATION", "SEZA_AND_SPEDU"]:
            acts_str = ", ".join(data["acts"])
            block = [f"### [{domain}] STATUTORY ANCHORS:\n- Legislation: {acts_str}"]
            
            if "mandatory_covenants" in data:
                covenants = "\n  * ".join(data["mandatory_covenants"])
                block.append(f"- Enforceable Baselines:\n  * {covenants}")
                
            if "clusters" in data:
                clusters = "\n  * ".join([f"{k}: {v}" for k, v in data["clusters"].items()])
                block.append(f"- SEZA Geographic Clusters:\n  * {clusters}")
                
            if "fiscal_rules" in data:
                rules = "\n  * ".join(data["fiscal_rules"])
                block.append(f"- Fiscal & Incentive Rules:\n  * {rules}")
                
            matched.append("\n".join(block))
            
    # Attach macroeconomic ground truth
    matched.append("### [EMPIRICAL MACROECONOMIC BENCHMARKS]:\n" + BOTSWANA_GROUND_TRUTH)
    return "\n\n".join(matched)
# ==============================================================================
# UPGRADE 1: SEZA 8-CLUSTER INDUSTRIAL MATRIX & EMPIRICAL MACRO BASELINES
# Codified from Special Economic Zones Act (Cap 44:03) & National Integrated Resource Plan
# ==============================================================================

SEZA_INDUSTRIAL_CLUSTERS = {
    "SSKIA": {
        "name": "Sir Seretse Khama International Airport (SSKIA) Special Economic Zone",
        "focus": ["Diamond Beneficiation", "Jewelry Manufacturing", "Air Cargo Logistics", "High-Value Electronics", "Aerospace Support"],
        "minimum_capex_pula": 50000000.0,
        "statutory_anchor": "Special Economic Zones Act [Cap 44:03] Sec 14",
        "mandatory_covenants": [
            "Rough diamond local cut-and-polish quota via Okavango Diamond Company (ODC)",
            "Air freight bonded transit integration within 5km of SSKIA cargo terminal"
        ]
    },
    "FAIRGROUNDS": {
        "name": "Gaborone Fairgrounds Financial Technology & IFSC Zone",
        "focus": ["International Financial Services Centre (IFSC)", "Fintech Software Engines", "B2B Data Routing", "Risk Underwriting"],
        "minimum_capex_pula": 25000000.0,
        "statutory_anchor": "Income Tax Act (IFSC 15% Concessionary Rate) & FIA 2022",
        "mandatory_covenants": [
            "Domestic Tier-3 data hosting compliance under Data Protection Act",
            "Zero offshore data leak covenants for sovereign financial telemetry"
        ]
    },
    "LOBATSE": {
        "name": "Lobatse Meat & Leather Processing Cluster",
        "focus": ["Beef By-Products Processing", "Leather Tannery", "Biogas & Effluent Cogeneration", "Cold Chain Logistics"],
        "minimum_capex_pula": 30000000.0,
        "statutory_anchor": "Botswana Meat Commission Act & Industrial Development Act",
        "mandatory_covenants": [
            "100% industrial tannery effluent pre-treatment prior to municipal discharge",
            "Mandatory domestic hide off-take priority over raw wet-blue exports"
        ]
    },
    "SELEBI_PHIKWE": {
        "name": "Selebi-Phikwe Heavy Metallurgy & Green Industrial Revitalization (SPEDU)",
        "focus": ["Base Metal Smelting (Copper/Nickel Salvage)", "Scrap Steel Smelting", "Agro-Chemical Manufacturing", "Apparel Garments"],
        "minimum_capex_pula": 40000000.0,
        "statutory_anchor": "SPEDU Special Incentive Framework & Mines and Minerals Act [Cap 66:01]",
        "mandatory_covenants": [
            "5% corporate tax rate adherence for eligible SPEDU manufacturing pioneers",
            "Solvent extraction / electrowinning (SX-EW) clean tailing recovery protocol"
        ]
    },
    "PANDAMATENGA": {
        "name": "Pandamatenga Commercial Agro-Industrial Hub",
        "focus": ["Sorghum Milling", "Sunflower & Soya Oil Extraction", "Silo Grain Infrastructure", "Export Grade Pulses"],
        "minimum_capex_pula": 35000000.0,
        "statutory_anchor": "National Agricultural Policy & BAMB Strategic Reserve Act",
        "mandatory_covenants": [
            "Mandatory 30% domestic farmer outgrower off-take contract covenant",
            "P9.2B import substitution compliance (substitutes edible oil / grain grain tariffs)"
        ]
    },
    "FRANCISTOWN": {
        "name": "Francistown Multi-Modal Transport, Mining Logistics & Dry Port",
        "focus": ["SADC Rail-to-Road Freight Intermodal Transshipment", "Heavy Mining Equipment Overhaul", "Warehouse Distribution"],
        "minimum_capex_pula": 30000000.0,
        "statutory_anchor": "Railway Act & Customs and Excise Duty Act",
        "mandatory_covenants": [
            "Kazungula bridge corridor customs pre-clearance integration",
            "Minimum 50% citizen-owned road freight subcontracting under CEE Act 2021"
        ]
    },
    "PALAPYE": {
        "name": "Palapye Energy, Petrochemical & Coal-Bed Methane (CBM) Sector",
        "focus": ["Clean Coal Gasification", "Captive Solar PV Baseloads", "Coal-Bed Methane (CBM) to Liquids", "Glass Manufacturing"],
        "minimum_capex_pula": 60000000.0,
        "statutory_anchor": "BERA Act 2016 & Mines and Minerals Act [Cap 66:01]",
        "mandatory_covenants": [
            "30% solar captive offset for energy generation exceeding 5MW baseload",
            "Zero methane flaring; capture required for domestic grid feed-in"
        ]
    },
    "TULI_BLOCK": {
        "name": "Tuli Block High-Yield Precision Horticulture Hub",
        "focus": ["Citrus Production", "Drip-Irrigated Vegetable Processing", "Cold-Storage Aggregation", "Export Packing"],
        "minimum_capex_pula": 20000000.0,
        "statutory_anchor": "Water Act [Cap 34:01] & Agrochemicals Act",
        "mandatory_covenants": [
            "Closed-loop drip irrigation water efficiency exceeding 90%",
            "Limpopo river water basin quota abstraction compliance verified by WUC"
        ]
    }
}

NATIONAL_MACRO_DEFICITS = {
    "FOOD_IMPORT_BILL_BWP": 9200000000.0,  # P9.2 Billion annual food import deficit
    "DOMESTIC_CROP_YIELD_PCT": 17.3,       # National cereal demand met locally
    "NATIONAL_UNEMPLOYMENT_RATE_PCT": 27.6, # Overall national baseline
    "YOUTH_UNEMPLOYMENT_RATE_PCT": 38.0,    # Youth baseline
    "CEE_MINIMUM_LOCAL_SUBCONTRACT_PCT": 50.0, # Citizen Economic Inclusion Act
    "CITIZEN_RESERVED_SECTORS_COUNT": 35   # 35 Exclusive citizen commerce sectors
}

NATIONAL_ENERGY_BASELINE_IRP = {
    "ANNUAL_SUNSHINE_HOURS": 3200,          # High direct normal irradiance (DNI)
    "IRP_2030_RENEWABLE_TARGET_PCT": 30.0,   # Integrated Resource Plan requirement
    "CAPTIVE_SOLAR_PV_MANDATE_KW_THRESHOLD": 1000.0, # 1MW+ facilities mandate offset
    "WATER_UTILITIES_CORPORATION_EFFLUENT_REUSE_PCT": 100.0 # WUC mandate on heavy industry
}
