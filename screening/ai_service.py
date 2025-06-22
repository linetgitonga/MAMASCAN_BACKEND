# screening/ai_service.py
import joblib
import numpy as np
import os
from django.conf import settings
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)

class CervicalCancerRiskPredictor:
    """AI service for cervical cancer risk prediction"""
    
    def __init__(self):
        self.model = None
        self.feature_names = [
            'age', 'age_at_first_intercourse', 'number_of_sexual_partners',
            'parity', 'hiv_positive', 'hpv_vaccinated', 'contraceptive_use_encoded',
            'smoking_current', 'smoking_former', 'family_history',
            'previous_abnormal_pap', 'via_positive', 'via_suspicious',
            'bethesda_ascus', 'bethesda_lsil', 'bethesda_hsil', 
            'bethesda_agc', 'bethesda_cancer'
        ]
        self.load_model()
    
    def load_model(self):
        """Load the trained AI model"""
        try:
            model_path = os.path.join(
                settings.AI_MODEL_PATH, 
                settings.RISK_PREDICTION_MODEL
            )
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                logger.info("AI model loaded successfully")
            else:
                logger.warning("AI model file not found, using fallback logic")
                self.model = None
        except Exception as e:
            logger.error(f"Error loading AI model: {e}")
            self.model = None
    
    def preprocess_input(self, data: Dict) -> np.ndarray:
        """Preprocess input data for model prediction"""
        features = np.zeros(len(self.feature_names))
        
        # Basic demographics and risk factors
        features[0] = data.get('age', 30)
        features[1] = data.get('age_at_first_intercourse', 18)
        features[2] = data.get('number_of_sexual_partners', 1)
        features[3] = data.get('parity', 0)
        
        # HIV status
        features[4] = 1 if data.get('hiv_status') == 'POSITIVE' else 0
        
        # HPV vaccination
        features[5] = 1 if data.get('hpv_vaccination_status') == 'VACCINATED' else 0
        
        # Contraceptive use (encoded as risk level)
        contraceptive_risk = {
            'NONE': 0, 'BARRIER': 1, 'IUD': 2, 
            'INJECTION': 3, 'ORAL_PILLS': 4, 'OTHER': 2
        }
        features[6] = contraceptive_risk.get(data.get('contraceptive_use', 'NONE'), 0)
        
        # Smoking status
        smoking = data.get('smoking_status', 'NEVER')
        features[7] = 1 if smoking == 'CURRENT' else 0
        features[8] = 1 if smoking == 'FORMER' else 0
        
        # Medical history
        features[9] = 1 if data.get('family_history_cervical_cancer', False) else 0
        features[10] = 1 if data.get('previous_abnormal_pap', False) else 0
        
        # VIA results
        via_result = data.get('via_result')
        features[11] = 1 if via_result == 'POSITIVE' else 0
        features[12] = 1 if via_result == 'SUSPICIOUS' else 0
        
        # Bethesda categories
        bethesda = data.get('bethesda_category')
        bethesda_mapping = {
            'ASCUS': 13, 'LSIL': 14, 'HSIL': 15, 
            'AGC': 16, 'CANCER': 17
        }
        if bethesda in bethesda_mapping:
            features[bethesda_mapping[bethesda]] = 1
        
        return features.reshape(1, -1)
    
    def calculate_risk_score(self, data: Dict) -> float:
        """Calculate risk score using rule-based or ML approach"""
        if self.model is not None:
            try:
                features = self.preprocess_input(data)
                risk_score = self.model.predict_proba(features)[0][1]  # Probability of high risk
                return float(risk_score)
            except Exception as e:
                logger.error(f"Error in ML prediction: {e}")
                return self._fallback_risk_calculation(data)
        else:
            return self._fallback_risk_calculation(data)
    
    def _fallback_risk_calculation(self, data: Dict) -> float:
        """Fallback rule-based risk calculation when ML model is unavailable"""
        risk_score = 0.1  # Base risk
        
        # Age factor
        age = data.get('age', 30)
        if age > 50:
            risk_score += 0.2
        elif age > 35:
            risk_score += 0.1
        
        # Sexual history
        age_first_intercourse = data.get('age_at_first_intercourse', 18)
        if age_first_intercourse < 16:
            risk_score += 0.15
        
        partners = data.get('number_of_sexual_partners', 1)
        if partners > 4:
            risk_score += 0.2
        elif partners > 2:
            risk_score += 0.1
        
        # Parity
        parity = data.get('parity', 0)
        if parity > 5:
            risk_score += 0.15
        elif parity > 3:
            risk_score += 0.1
        
        # HIV status
        if data.get('hiv_status') == 'POSITIVE':
            risk_score += 0.25
        
        # HPV vaccination (protective)
        if data.get('hpv_vaccination_status') == 'VACCINATED':
            risk_score -= 0.1
        
        # Smoking
        if data.get('smoking_status') == 'CURRENT':
            risk_score += 0.15
        elif data.get('smoking_status') == 'FORMER':
            risk_score += 0.05
        
        # Family history
        if data.get('family_history_cervical_cancer', False):
            risk_score += 0.1
        
        # Previous abnormal Pap
        if data.get('previous_abnormal_pap', False):
            risk_score += 0.2
        
        # VIA results
        via_result = data.get('via_result')
        if via_result == 'SUSPICIOUS':
            risk_score += 0.4
        elif via_result == 'POSITIVE':
            risk_score += 0.3
        
        # Bethesda categories
        bethesda = data.get('bethesda_category')
        bethesda_risks = {
            'CANCER': 0.9, 'HSIL': 0.6, 'AGC': 0.5,
            'LSIL': 0.3, 'ASCUS': 0.2
        }
        if bethesda in bethesda_risks:
            risk_score = max(risk_score, bethesda_risks[bethesda])
        
        return min(risk_score, 1.0)  # Cap at 1.0
    
    def classify_risk(self, risk_score: float) -> str:
        """Classify risk level based on score"""
        if risk_score >= 0.7:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def generate_recommendations(self, risk_level: str, data: Dict) -> Tuple[str, int, bool]:
        """Generate recommendations based on risk level and clinical data"""
        bethesda = data.get('bethesda_category')
        via_result = data.get('via_result')
        
        if risk_level == 'HIGH' or bethesda in ['HSIL', 'AGC', 'CANCER'] or via_result == 'SUSPICIOUS':
            return (
                "Urgent referral to specialist for colposcopy and biopsy. "
                "Immediate follow-up required.",
                1,  # 1 month follow-up
                True  # Referral needed
            )
        elif risk_level == 'MODERATE' or bethesda in ['LSIL', 'ASCUS'] or via_result == 'POSITIVE':
            return (
                "Repeat cytology in 6 months or refer for colposcopy. "
                "Close monitoring recommended.",
                6,  # 6 months follow-up
                True  # Referral may be needed
            )
        else:
            return (
                "Continue routine screening. Repeat screening in 3 years if low risk, "
                "or 1 year if any risk factors present.",
                36 if data.get('hiv_status') != 'POSITIVE' else 12,  # 3 years or 1 year for HIV+
                False  # No immediate referral needed
            )
    
    def get_risk_explanation(self, data: Dict, risk_score: float) -> List[str]:
        """Generate explanation for risk prediction"""
        explanations = []
        
        # High-impact factors
        if data.get('bethesda_category') in ['HSIL', 'AGC', 'CANCER']:
            explanations.append(f"High-grade abnormal cells detected ({data['bethesda_category']})")
        
        if data.get('via_result') == 'SUSPICIOUS':
            explanations.append("VIA test shows suspicious findings")
        
        if data.get('hiv_status') == 'POSITIVE':
            explanations.append("HIV positive status increases risk")
        
        # Moderate-impact factors
        if data.get('age', 30) > 50:
            explanations.append("Age over 50 increases risk")
        
        if data.get('number_of_sexual_partners', 1) > 4:
            explanations.append("Multiple sexual partners increase risk")
        
        if data.get('smoking_status') == 'CURRENT':
            explanations.append("Current smoking increases risk")
        
        if data.get('family_history_cervical_cancer', False):
            explanations.append("Family history of cervical cancer")
        
        # Protective factors
        if data.get('hpv_vaccination_status') == 'VACCINATED':
            explanations.append("HPV vaccination provides protection")
        
        if not explanations:
            explanations.append("Low risk based on current screening results and risk factors")
        
        return explanations
    
    def predict(self, data: Dict) -> Dict:
        """Main prediction method"""
        try:
            risk_score = self.calculate_risk_score(data)
            risk_level = self.classify_risk(risk_score)
            recommended_action, follow_up_months, referral_needed = self.generate_recommendations(
                risk_level, data
            )
            explanations = self.get_risk_explanation(data, risk_score)
            
            # Calculate confidence (simplified approach)
            confidence = 0.9 if self.model is not None else 0.7
            
            return {
                'risk_score': round(risk_score, 3),
                'risk_level': risk_level,
                'confidence': confidence,
                'recommended_action': recommended_action,
                'follow_up_months': follow_up_months,
                'referral_needed': referral_needed,
                'explanation': explanations
            }
        
        except Exception as e:
            logger.error(f"Error in risk prediction: {e}")
            return {
                'risk_score': 0.5,
                'risk_level': 'MODERATE',
                'confidence': 0.5,
                'recommended_action': 'Unable to complete risk assessment. Please consult healthcare provider.',
                'follow_up_months': 6,
                'referral_needed': True,
                'explanation': ['Risk assessment incomplete due to technical error']
            }

# Singleton instance
risk_predictor = CervicalCancerRiskPredictor()