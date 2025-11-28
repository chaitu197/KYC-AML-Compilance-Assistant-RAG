"""
Transaction Risk Scoring Module
Analyzes transactions and queries for AML/KYC compliance risks
"""

from typing import Dict, List
from datetime import datetime
import json


# High-risk countries (simplified list - expand as needed)
HIGH_RISK_COUNTRIES = [
    'Afghanistan', 'Iran', 'North Korea', 'Syria', 'Yemen',
    'Myanmar', 'Cuba', 'Sudan', 'Venezuela'
]

# Risk keywords for compliance
HIGH_RISK_KEYWORDS = [
    'sanction', 'terrorist', 'terrorism', 'fraud', 'laundering',
    'money laundering', 'shell company', 'offshore', 'pep',
    'politically exposed', 'blacklist', 'watchlist'
]

MEDIUM_RISK_KEYWORDS = [
    'cash', 'cryptocurrency', 'bitcoin', 'anonymous', 'bearer',
    'structuring', 'smurfing', 'layering', 'placement'
]


def calculate_transaction_risk(transaction_data: Dict) -> Dict:
    """
    Calculate risk score for a transaction.
    
    Args:
        transaction_data: Dict with keys:
            - amount: float
            - currency: str
            - country: str
            - count_24h: int (transactions in last 24h)
            - customer_type: str (individual/corporate)
            - is_cash: bool
            
    Returns:
        Dict with risk_score (0-100), risk_level, and flags
    """
    risk_score = 0
    flags = []
    
    # Amount-based risk
    amount = transaction_data.get('amount', 0)
    if amount >= 50000:
        risk_score += 35
        flags.append(f"High-value transaction: ${amount:,.2f}")
    elif amount >= 10000:
        risk_score += 20
        flags.append(f"Medium-value transaction: ${amount:,.2f}")
    
    # Velocity risk
    count_24h = transaction_data.get('count_24h', 0)
    if count_24h > 20:
        risk_score += 30
        flags.append(f"Very high velocity: {count_24h} transactions/24h")
    elif count_24h > 10:
        risk_score += 15
        flags.append(f"High velocity: {count_24h} transactions/24h")
    
    # Geographic risk
    country = transaction_data.get('country', '')
    if country in HIGH_RISK_COUNTRIES:
        risk_score += 25
        flags.append(f"High-risk jurisdiction: {country}")
    
    # Cash transaction risk
    if transaction_data.get('is_cash', False):
        risk_score += 15
        flags.append("Cash transaction")
    
    # Customer type risk
    if transaction_data.get('customer_type') == 'corporate':
        if amount < 1000:
            risk_score += 10
            flags.append("Unusual small corporate transaction")
    
    # Cap at 100
    risk_score = min(risk_score, 100)
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = "HIGH"
        action = "Enhanced Due Diligence Required"
    elif risk_score >= 40:
        risk_level = "MEDIUM"
        action = "Standard Due Diligence Required"
    else:
        risk_level = "LOW"
        action = "Normal Processing"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "flags": flags,
        "recommended_action": action,
        "timestamp": datetime.now().isoformat()
    }


def analyze_query_risk(query: str) -> Dict:
    """
    Analyze a compliance query for risk indicators.
    
    Args:
        query: User's question
        
    Returns:
        Dict with risk assessment
    """
    query_lower = query.lower()
    risk_score = 0
    flags = []
    keywords_found = []
    
    # Check for high-risk keywords
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in query_lower:
            risk_score += 15
            keywords_found.append(keyword)
    
    # Check for medium-risk keywords
    for keyword in MEDIUM_RISK_KEYWORDS:
        if keyword in query_lower:
            risk_score += 8
            keywords_found.append(keyword)
    
    if keywords_found:
        flags.append(f"Risk keywords detected: {', '.join(keywords_found)}")
    
    # Cap at 100
    risk_score = min(risk_score, 100)
    
    # Determine risk level
    if risk_score >= 50:
        risk_level = "HIGH"
        alert = True
    elif risk_score >= 25:
        risk_level = "MEDIUM"
        alert = False
    else:
        risk_level = "LOW"
        alert = False
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "flags": flags,
        "keywords_found": keywords_found,
        "requires_alert": alert
    }


def generate_risk_report(transaction_data: Dict, query_risk: Dict) -> str:
    """Generate a formatted risk report."""
    report = f"""
# Risk Assessment Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Transaction Risk Analysis
- **Risk Score:** {transaction_data['risk_score']}/100
- **Risk Level:** {transaction_data['risk_level']}
- **Recommended Action:** {transaction_data['recommended_action']}

### Risk Flags:
"""
    for flag in transaction_data['flags']:
        report += f"- ⚠️ {flag}\n"
    
    if query_risk:
        report += f"""
## Query Risk Analysis
- **Risk Score:** {query_risk['risk_score']}/100
- **Risk Level:** {query_risk['risk_level']}
- **Alert Required:** {'Yes' if query_risk['requires_alert'] else 'No'}

### Keywords Detected:
"""
        for keyword in query_risk.get('keywords_found', []):
            report += f"- 🔍 {keyword}\n"
    
    return report


# Example usage
if __name__ == "__main__":
    # Test transaction risk
    test_transaction = {
        "amount": 55000,
        "currency": "USD",
        "country": "Iran",
        "count_24h": 15,
        "customer_type": "individual",
        "is_cash": True
    }
    
    result = calculate_transaction_risk(test_transaction)
    print(json.dumps(result, indent=2))
    
    # Test query risk
    test_query = "What are the requirements for terrorist financing detection?"
    query_result = analyze_query_risk(test_query)
    print(json.dumps(query_result, indent=2))
