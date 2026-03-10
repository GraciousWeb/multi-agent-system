from schema import Market
from pydantic import BaseModel, Field
from typing import List, Dict

class CritiquePolicy(BaseModel):
    market: Market
    focus: List[str]
    required_sources: List[str]
    red_flags: List[str]
    red_flag_scope: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Maps each red flag to the query types it applies to"
    )

POLICIES: Dict[Market, CritiquePolicy] = {
    "US": CritiquePolicy(
        market="US",
        focus=["SEC filings", "FinCEN updates", "Series A-E funding news"],
        required_sources=["sec.gov", "techcrunch.com", "reuters.com"],
        red_flags=["Unverified funding claims", "Lack of 8-K filings"],
        red_flag_scope={
            "Unverified funding claims": ["funding", "investment", "series", "valuation"],
            "Lack of 8-K filings":       ["sec", "filing", "public company", "earnings"]
        }
    ),
    "NG": CritiquePolicy(
        market="NG",
        focus=["CBN circulars", "SEC Nigeria approvals", "Naira stablecoin news"],
        required_sources=["cbn.gov.ng", "nairametrics.com", "techcabal.com"],
        red_flags=["No reference to CBN license", "Outdated funding dates"],
        red_flag_scope={
            "No reference to CBN license": ["regulation", "licensing", "compliance", "stablecoin"],
            "Outdated funding dates": ["funding", "investment", "series"]
        }
    ),
    "GLOBAL": CritiquePolicy(
        market="GLOBAL",
        focus=["Cross-border partnerships", "Global funding trends"],
        required_sources=["bloomberg.com", "reuters.com", "crunchbase.com", "bis.org", "fsb.org", "worldbank.org", "fatf-gafi.org", "finextra.com"],
        red_flags=["Single-source claims", "Dead links"],
        red_flag_scope={
            "Single-source claims": ["funding", "regulation", "partnership", "acquisition"],
            "Dead links":           [] 
        }
    ),
    "EU": CritiquePolicy(
        market="EU",
        focus=[
            "MiCA compliance for stablecoins", 
            "DORA (Digital Operational Resilience) audits", 
            "PSD3/PSR implementation", 
            "EU AI Act risk categorization"
        ],
        required_sources=["esma.europa.eu", "eba.europa.eu", "ec.europa.eu"],
        red_flags=[
            "Non-compliance with 'Verification of Payee' (VoP) rules", 
            "AI tools without transparency labels",
            "Cross-border 'Passporting' claims without local entity proof"
        ],
        red_flag_scope={
            "Non-compliance with 'Verification of Payee' (VoP) rules": ["payment", "transfer", "psd3", "open banking"],
            "AI tools without transparency labels":                      ["ai", "machine learning", "automated", "model"],
            "Cross-border 'Passporting' claims without local entity proof": ["passporting", "cross-border", "expansion", "licensing"]
        }
    ),
    "UK": CritiquePolicy(
        market="UK",
        focus=[
            "FCA Consumer Duty outcomes", 
            "Stablecoin/Crypto licensing progress", 
            "Open Banking (JROC) updates", 
            "SDR (Sustainability Disclosure) labels"
        ],
        required_sources=["fca.org.uk", "bankofengland.co.uk", "finextra.com", "sifted.eu"],
        red_flags=[
            "Claims of 'FCA Approved' for crypto (verify via FS Register)", 
            "Lack of Consumer Duty board report mention",
            "Confusion between EMI vs Banking licenses"
        ],
        red_flag_scope={
            "Claims of 'FCA Approved' for crypto (verify via FS Register)": ["crypto", "stablecoin", "digital asset", "token"],
            "Lack of Consumer Duty board report mention":                    ["consumer", "retail", "duty", "outcomes"],
            "Confusion between EMI vs Banking licenses":                     ["licensing", "emi", "banking", "payment institution"]
        }
    )
}