# Model Governance & Explainability Guide

## Table of Contents

1. [Introduction to Model Governance](#introduction-to-model-governance)
2. [Model Lifecycle Management](#model-lifecycle-management)
3. [Model Documentation](#model-documentation)
4. [Explainability & Interpretability](#explainability--interpretability)
5. [Bias & Fairness](#bias--fairness)
6. [Model Risk Management](#model-risk-management)
7. [Regulatory Compliance](#regulatory-compliance)
8. [Governance Framework](#governance-framework)

---

## 1. Introduction to Model Governance

**What is Model Governance?**

Model governance is the framework of policies, procedures, and controls that ensure ML models are:
- Developed responsibly
- Deployed safely
- Monitored continuously
- Compliant with regulations
- Explainable and auditable

**Why It Matters:**
- Regulatory requirements (GDPR, CCPA, Fair Credit Reporting Act)
- Risk management
- Stakeholder trust
- Ethical AI development
- Business value protection

---

## 2. Model Lifecycle Management

### 2.1 Model Registry & Versioning

**Implementation:**

```python
class ModelRegistry:
    """
    Centralized model registry for governance.

    Tracks:
    - Model versions
    - Training data versions
    - Code versions
    - Performance metrics
    - Approval status
    - Deployment history
    """

    def register_model(
        self,
        model_name: str,
        model_artifact: Any,
        training_data_version: str,
        code_version: str,
        metrics: Dict[str, float],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Register model with full lineage.

        Returns:
            model_version: Unique version identifier
        """
        model_version = self.generate_version()

        model_record = {
            'name': model_name,
            'version': model_version,
            'artifact_path': self.store_artifact(model_artifact),
            'training_data_version': training_data_version,
            'code_version': code_version,
            'git_commit': self.get_git_commit(),
            'metrics': metrics,
            'metadata': metadata,
            'created_at': datetime.utcnow(),
            'created_by': self.get_current_user(),
            'status': 'development',  # development -> staging -> production
            'approval_status': 'pending'
        }

        self.store_model_record(model_record)

        return model_version

    def get_model_lineage(self, model_version: str) -> Dict:
        """
        Get complete lineage for model version.

        Returns lineage graph showing:
        - Training data → Features → Model → Predictions
        - Code versions
        - Related models
        """
        lineage = {
            'model': self.get_model_record(model_version),
            'training_data': self.get_data_lineage(model_version),
            'code': self.get_code_lineage(model_version),
            'dependencies': self.get_dependencies(model_version),
            'downstream_models': self.get_downstream_models(model_version),
            'predictions': self.get_prediction_history(model_version)
        }

        return lineage
```

### 2.2 Model Approval Workflow

```python
class ModelApprovalWorkflow:
    """
    Multi-stage approval process for model deployment.

    Stages:
    1. Development: Model training
    2. Validation: Technical review
    3. Staging: Business validation
    4. Production: Approved for deployment
    5. Archived: Deprecated
    """

    def request_approval(
        self,
        model_version: str,
        target_stage: str,
        justification: str
    ):
        """Request approval to promote model to next stage."""

        approval_request = {
            'model_version': model_version,
            'current_stage': self.get_model_stage(model_version),
            'target_stage': target_stage,
            'requested_by': self.get_current_user(),
            'requested_at': datetime.utcnow(),
            'justification': justification,
            'status': 'pending'
        }

        # Assign approvers based on target stage
        if target_stage == 'staging':
            approval_request['approvers'] = ['tech_lead']
        elif target_stage == 'production':
            approval_request['approvers'] = ['tech_lead', 'product_manager', 'compliance_officer']

        self.create_approval_request(approval_request)

        # Notify approvers
        self.notify_approvers(approval_request)

    def approve_model(
        self,
        approval_id: str,
        approver: str,
        comments: str
    ):
        """Approve model for promotion."""

        approval = self.get_approval_request(approval_id)

        if approver not in approval['approvers']:
            raise ValueError("Not authorized to approve")

        # Record approval
        self.record_approval(approval_id, approver, comments)

        # Check if all approvers have approved
        if self.all_approved(approval_id):
            # Promote model
            self.promote_model(
                approval['model_version'],
                approval['target_stage']
            )

            # Notify stakeholders
            self.notify_promotion(approval)

    def get_approval_checklist(self, target_stage: str) -> List[Dict]:
        """Get required checks for stage promotion."""

        checklists = {
            'staging': [
                {'check': 'Unit tests pass', 'required': True},
                {'check': 'Integration tests pass', 'required': True},
                {'check': 'Performance meets SLA', 'required': True},
                {'check': 'Model card completed', 'required': True},
                {'check': 'Bias assessment done', 'required': True}
            ],
            'production': [
                {'check': 'Staging validation successful', 'required': True},
                {'check': 'A/B test results positive', 'required': True},
                {'check': 'Rollback plan documented', 'required': True},
                {'check': 'Monitoring configured', 'required': True},
                {'check': 'Business sign-off', 'required': True},
                {'check': 'Security review passed', 'required': True},
                {'check': 'Compliance review passed', 'required': True}
            ]
        }

        return checklists.get(target_stage, [])
```

---

## 3. Model Documentation

### 3.1 Model Cards

**Template:**

```markdown
# Model Card: [Model Name]

## Model Details
- **Developer**: [Team/Person]
- **Model Date**: [YYYY-MM-DD]
- **Model Version**: [x.y.z]
- **Model Type**: [Algorithm]
- **Paper/Resource**: [Link to methodology]
- **License**: [License type]
- **Contact**: [email/slack]

## Intended Use
- **Primary intended uses**: [What is this model for?]
- **Primary intended users**: [Who will use it?]
- **Out-of-scope use cases**: [What should it NOT be used for?]

## Training Data
- **Dataset(s)**: [Name and source]
- **Motivation**: [Why this data?]
- **Preprocessing**: [What was done to data?]
- **Sample Size**: [N samples, features]
- **Time Period**: [YYYY-MM-DD to YYYY-MM-DD]
- **Geographic Coverage**: [Where is data from?]
- **Known Limitations**: [Data quality issues, biases]

## Evaluation Data
- **Dataset(s)**: [Test set description]
- **Motivation**: [Why this test set?]
- **Preprocessing**: [Same as training?]

## Model Performance

### Aggregate Metrics
| Metric | Value |
|--------|-------|
| Accuracy | 0.87 |
| Precision | 0.85 |
| Recall | 0.83 |
| F1-Score | 0.84 |
| ROC-AUC | 0.91 |

### Performance by Subgroup
| Group | Accuracy | Precision | Recall |
|-------|----------|-----------|--------|
| Group A | 0.88 | 0.86 | 0.84 |
| Group B | 0.86 | 0.84 | 0.82 |
| Group C | 0.87 | 0.85 | 0.83 |

### Intersectional Performance
[If analyzing intersectional fairness]

## Ethical Considerations
- **Sensitive Data**: [What sensitive attributes used?]
- **Human Life**: [Impact on human life?]
- **Risks**: [What are the risks?]
- **Mitigations**: [What did you do about risks?]
- **Use Cases to Monitor**: [What should be watched?]

## Caveats and Recommendations
- [What are limitations?]
- [What assumptions were made?]
- [What would you do differently with more resources?]
- [What additional work is needed?]
```

### 3.2 Model Documentation Checklist

```python
class ModelDocumentation:
    """Ensure complete model documentation."""

    def validate_documentation(self, model_version: str) -> Dict:
        """
        Check if model documentation is complete.

        Returns:
            {
                'complete': True/False,
                'missing': [list of missing items],
                'warnings': [list of warnings]
            }
        """
        required_docs = [
            'model_card',
            'training_data_description',
            'evaluation_metrics',
            'intended_use',
            'limitations',
            'bias_assessment',
            'performance_by_group'
        ]

        documentation = self.get_model_documentation(model_version)

        missing = [
            doc for doc in required_docs
            if doc not in documentation or not documentation[doc]
        ]

        warnings = []

        # Check quality of documentation
        if 'limitations' in documentation:
            if len(documentation['limitations']) < 100:  # chars
                warnings.append("Limitations section too brief")

        if 'bias_assessment' in documentation:
            if 'subgroup_performance' not in documentation['bias_assessment']:
                warnings.append("Missing subgroup performance analysis")

        return {
            'complete': len(missing) == 0,
            'missing': missing,
            'warnings': warnings
        }
```

---

## 4. Explainability & Interpretability

### 4.1 SHAP (SHapley Additive exPlanations)

```python
import shap
import numpy as np
import pandas as pd

class SHAPExplainer:
    """
    Generate SHAP-based explanations.

    SHAP provides:
    - Feature importance (global)
    - Feature contributions (local)
    - Interaction effects
    - Consistent and theoretically grounded
    """

    def __init__(self, model, data):
        """Initialize SHAP explainer."""
        # Choose appropriate explainer type
        if hasattr(model, 'tree_'):  # Tree-based
            self.explainer = shap.TreeExplainer(model)
        else:  # Model-agnostic
            self.explainer = shap.KernelExplainer(
                model.predict_proba,
                shap.sample(data, 100)  # Background dataset
            )

    def explain_prediction(self, instance, feature_names):
        """
        Explain single prediction.

        Returns:
            {
                'prediction': model output,
                'base_value': average prediction,
                'feature_contributions': dict of feature → contribution
            }
        """
        shap_values = self.explainer.shap_values(instance)

        # For binary classification, use positive class
        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        explanation = {
            'prediction': self.model.predict(instance)[0],
            'base_value': self.explainer.expected_value,
            'feature_contributions': dict(zip(
                feature_names,
                shap_values[0] if len(shap_values.shape) > 1 else shap_values
            ))
        }

        return explanation

    def get_global_importance(self, data, feature_names):
        """
        Get global feature importance.

        Returns:
            DataFrame with features ranked by importance
        """
        shap_values = self.explainer.shap_values(data)

        # Mean absolute SHAP value per feature
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Positive class

        importance = np.abs(shap_values).mean(axis=0)

        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)

        return importance_df

    def generate_waterfall_plot(self, instance, feature_names, output_file):
        """Generate waterfall plot showing contribution of each feature."""
        shap_values = self.explainer.shap_values(instance)

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap.waterfall_plot(
            shap.Explanation(
                values=shap_values[0],
                base_values=self.explainer.expected_value,
                data=instance[0],
                feature_names=feature_names
            )
        )

        plt.savefig(output_file)

    def generate_force_plot(self, instance, feature_names, output_file):
        """Generate force plot visualization."""
        shap_values = self.explainer.shap_values(instance)

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap.force_plot(
            self.explainer.expected_value,
            shap_values[0],
            instance[0],
            feature_names=feature_names,
            matplotlib=True
        )

        plt.savefig(output_file)
```

### 4.2 Natural Language Explanations

```python
class NaturalLanguageExplainer:
    """
    Convert technical explanations to natural language.

    Makes explanations accessible to non-technical stakeholders.
    """

    def generate_explanation(
        self,
        prediction: float,
        feature_contributions: Dict[str, float],
        confidence: float,
        threshold: float = 0.5
    ) -> str:
        """
        Generate natural language explanation.

        Args:
            prediction: Model prediction
            feature_contributions: SHAP values per feature
            confidence: Prediction confidence
            threshold: Decision threshold

        Returns:
            Human-readable explanation string
        """
        # Sort features by contribution magnitude
        sorted_features = sorted(
            feature_contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        # Start explanation
        decision = "approve" if prediction >= threshold else "deny"
        confidence_text = self._confidence_level(confidence)

        explanation = f"Decision: {decision.upper()} ({confidence_text} confidence: {confidence:.1%})\n\n"

        explanation += "This decision was primarily based on:\n\n"

        # Explain top 5 contributing features
        for feature, contribution in sorted_features[:5]:
            direction = "increased" if contribution > 0 else "decreased"
            strength = self._contribution_strength(abs(contribution))

            explanation += f"• {feature.replace('_', ' ').title()}: "
            explanation += f"{strength} {direction} the approval probability\n"

        # Add context
        explanation += "\n"
        explanation += f"Baseline approval rate: {self.baseline_rate:.1%}\n"
        explanation += f"This application: {prediction:.1%}\n"

        return explanation

    def _confidence_level(self, confidence: float) -> str:
        """Convert confidence score to text."""
        if confidence > 0.9:
            return "very high"
        elif confidence > 0.75:
            return "high"
        elif confidence > 0.6:
            return "moderate"
        else:
            return "low"

    def _contribution_strength(self, magnitude: float) -> str:
        """Convert contribution magnitude to text."""
        if magnitude > 0.5:
            return "strongly"
        elif magnitude > 0.2:
            return "moderately"
        else:
            return "slightly"
```

### 4.3 Counterfactual Explanations

```python
class CounterfactualExplainer:
    """
    Generate counterfactual explanations.

    Answers: "What would need to change for a different outcome?"

    Example: "If income was $5,000 higher, the application would be approved."
    """

    def generate_counterfactual(
        self,
        model,
        instance: np.ndarray,
        desired_outcome: int,
        feature_names: List[str],
        mutable_features: List[str],
        max_changes: int = 3
    ) -> Dict:
        """
        Find minimal changes to flip prediction.

        Args:
            model: Trained model
            instance: Current instance
            desired_outcome: Target prediction
            feature_names: Names of all features
            mutable_features: Features that can be changed
            max_changes: Maximum number of features to change

        Returns:
            {
                'original_prediction': current prediction,
                'counterfactual_prediction': new prediction,
                'changes': {feature: (old_value, new_value)}
            }
        """
        # Simple greedy search for counterfactual
        current = instance.copy()
        original_pred = model.predict(current)[0]

        changes = {}
        mutable_indices = [
            i for i, name in enumerate(feature_names)
            if name in mutable_features
        ]

        for _ in range(max_changes):
            best_feature = None
            best_value = None
            best_distance = float('inf')

            # Try changing each mutable feature
            for idx in mutable_indices:
                if idx in changes:
                    continue  # Already changed

                # Try different values
                for delta in [-0.5, -0.25, 0.25, 0.5, 1.0]:
                    candidate = current.copy()
                    candidate[0, idx] += delta

                    pred = model.predict(candidate)[0]

                    if pred == desired_outcome:
                        distance = abs(delta)
                        if distance < best_distance:
                            best_distance = distance
                            best_feature = idx
                            best_value = candidate[0, idx]

            if best_feature is None:
                break  # No beneficial changes found

            # Apply best change
            old_value = current[0, best_feature]
            current[0, best_feature] = best_value
            changes[feature_names[best_feature]] = (old_value, best_value)

            # Check if goal achieved
            if model.predict(current)[0] == desired_outcome:
                break

        counterfactual_pred = model.predict(current)[0]

        return {
            'original_prediction': original_pred,
            'counterfactual_prediction': counterfactual_pred,
            'changes': changes,
            'success': counterfactual_pred == desired_outcome
        }

    def explain_counterfactual(self, counterfactual: Dict) -> str:
        """Generate natural language explanation of counterfactual."""

        if not counterfactual['success']:
            return "Could not find changes that would flip the prediction."

        explanation = "To change the outcome:\n\n"

        for feature, (old_value, new_value) in counterfactual['changes'].items():
            change = new_value - old_value
            direction = "increase" if change > 0 else "decrease"

            explanation += f"• {feature.replace('_', ' ').title()}: "
            explanation += f"{direction} from {old_value:.2f} to {new_value:.2f}\n"

        return explanation
```

---

## 5. Bias & Fairness

### 5.1 Fairness Metrics

```python
class FairnessAnalyzer:
    """
    Analyze model fairness across demographic groups.

    Fairness Metrics:
    - Demographic Parity: P(Ŷ=1|A=0) = P(Ŷ=1|A=1)
    - Equal Opportunity: P(Ŷ=1|Y=1,A=0) = P(Ŷ=1|Y=1,A=1)
    - Equalized Odds: Equal TPR and FPR across groups
    - Predictive Parity: P(Y=1|Ŷ=1,A=0) = P(Y=1|Ŷ=1,A=1)
    """

    def analyze_fairness(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        protected_attribute: np.ndarray,
        favorable_label: int = 1
    ) -> Dict:
        """
        Comprehensive fairness analysis.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            protected_attribute: Sensitive attribute (e.g., gender, race)
            favorable_label: Which prediction is favorable

        Returns:
            Dictionary with fairness metrics per group
        """
        groups = np.unique(protected_attribute)

        results = {
            'demographic_parity': {},
            'equal_opportunity': {},
            'equalized_odds': {},
            'predictive_parity': {},
            'disparate_impact': {}
        }

        # Calculate metrics for each group
        group_metrics = {}
        for group in groups:
            mask = protected_attribute == group

            group_metrics[group] = {
                'positive_rate': (y_pred[mask] == favorable_label).mean(),
                'tpr': self._tpr(y_true[mask], y_pred[mask], favorable_label),
                'fpr': self._fpr(y_true[mask], y_pred[mask], favorable_label),
                'precision': self._precision(y_true[mask], y_pred[mask], favorable_label)
            }

        # Demographic Parity
        positive_rates = [m['positive_rate'] for m in group_metrics.values()]
        results['demographic_parity']['difference'] = max(positive_rates) - min(positive_rates)
        results['demographic_parity']['ratio'] = min(positive_rates) / max(positive_rates)

        # Equal Opportunity
        tprs = [m['tpr'] for m in group_metrics.values()]
        results['equal_opportunity']['difference'] = max(tprs) - min(tprs)

        # Equalized Odds
        fprs = [m['fpr'] for m in group_metrics.values()]
        results['equalized_odds']['tpr_difference'] = max(tprs) - min(tprs)
        results['equalized_odds']['fpr_difference'] = max(fprs) - min(fprs)

        # Predictive Parity
        precisions = [m['precision'] for m in group_metrics.values()]
        results['predictive_parity']['difference'] = max(precisions) - min(precisions)

        # Disparate Impact
        # Ratio of positive rates (should be close to 1.0)
        results['disparate_impact']['ratio'] = min(positive_rates) / max(positive_rates)

        # Add per-group metrics
        results['per_group'] = group_metrics

        # Overall assessment
        results['is_fair'] = self._assess_fairness(results)

        return results

    def _tpr(self, y_true, y_pred, positive_label):
        """True Positive Rate (Recall)."""
        tp = ((y_true == positive_label) & (y_pred == positive_label)).sum()
        p = (y_true == positive_label).sum()
        return tp / p if p > 0 else 0

    def _fpr(self, y_true, y_pred, positive_label):
        """False Positive Rate."""
        fp = ((y_true != positive_label) & (y_pred == positive_label)).sum()
        n = (y_true != positive_label).sum()
        return fp / n if n > 0 else 0

    def _precision(self, y_true, y_pred, positive_label):
        """Precision (Predictive Parity)."""
        tp = ((y_true == positive_label) & (y_pred == positive_label)).sum()
        pp = (y_pred == positive_label).sum()
        return tp / pp if pp > 0 else 0

    def _assess_fairness(self, results: Dict) -> bool:
        """
        Assess if model meets fairness criteria.

        Common thresholds:
        - Demographic parity difference < 0.1 (10%)
        - Disparate impact ratio > 0.8 (80% rule)
        - Equal opportunity difference < 0.1
        """
        return (
            results['demographic_parity']['difference'] < 0.1 and
            results['disparate_impact']['ratio'] > 0.8 and
            results['equal_opportunity']['difference'] < 0.1
        )

    def generate_fairness_report(self, results: Dict) -> str:
        """Generate human-readable fairness report."""
        report = "=" * 60 + "\n"
        report += "FAIRNESS ANALYSIS REPORT\n"
        report += "=" * 60 + "\n\n"

        report += f"Overall Assessment: {'FAIR' if results['is_fair'] else 'POTENTIAL BIAS DETECTED'}\n\n"

        report += "Demographic Parity:\n"
        report += f"  Difference: {results['demographic_parity']['difference']:.4f} (< 0.10 is fair)\n\n"

        report += "Disparate Impact:\n"
        report += f"  Ratio: {results['disparate_impact']['ratio']:.4f} (> 0.80 is fair)\n\n"

        report += "Equal Opportunity:\n"
        report += f"  TPR Difference: {results['equal_opportunity']['difference']:.4f} (< 0.10 is fair)\n\n"

        report += "Per-Group Metrics:\n"
        for group, metrics in results['per_group'].items():
            report += f"\n  Group {group}:\n"
            report += f"    Positive Rate: {metrics['positive_rate']:.4f}\n"
            report += f"    TPR (Recall): {metrics['tpr']:.4f}\n"
            report += f"    FPR: {metrics['fpr']:.4f}\n"
            report += f"    Precision: {metrics['precision']:.4f}\n"

        return report
```

### 5.2 Bias Mitigation

```python
class BiasMitigation:
    """
    Techniques to mitigate bias in ML models.

    Approaches:
    - Pre-processing: Fix biased training data
    - In-processing: Modify learning algorithm
    - Post-processing: Adjust predictions
    """

    def reweight_samples(
        self,
        X: np.ndarray,
        y: np.ndarray,
        protected_attribute: np.ndarray
    ) -> np.ndarray:
        """
        Pre-processing: Reweight training samples to achieve fairness.

        Gives higher weight to underrepresented group/label combinations.
        """
        from sklearn.utils.class_weight import compute_sample_weight

        # Create combined attribute (group, label)
        combined = [
            f"{group}_{label}"
            for group, label in zip(protected_attribute, y)
        ]

        # Compute weights to balance
        weights = compute_sample_weight('balanced', combined)

        return weights

    def fair_classifier(
        self,
        base_model,
        fairness_constraint: str = 'demographic_parity'
    ):
        """
        In-processing: Train model with fairness constraints.

        Uses fairness-aware learning algorithms.
        """
        # Placeholder for fair learning algorithms
        # Real implementation would use libraries like:
        # - AIF360 (AI Fairness 360)
        # - Fairlearn
        # - Themis-ml

        pass

    def threshold_optimization(
        self,
        model,
        X: np.ndarray,
        y: np.ndarray,
        protected_attribute: np.ndarray
    ) -> Dict[str, float]:
        """
        Post-processing: Optimize thresholds per group to achieve fairness.

        Returns different decision thresholds for each group.
        """
        groups = np.unique(protected_attribute)
        thresholds = {}

        # Get prediction probabilities
        y_prob = model.predict_proba(X)[:, 1]

        # Find optimal threshold for each group
        for group in groups:
            mask = protected_attribute == group

            # Try different thresholds
            best_threshold = 0.5
            best_metric = 0

            for threshold in np.linspace(0.1, 0.9, 50):
                y_pred = (y_prob[mask] >= threshold).astype(int)

                # Optimize for F1 score (or other metric)
                f1 = self._f1_score(y[mask], y_pred)

                if f1 > best_metric:
                    best_metric = f1
                    best_threshold = threshold

            thresholds[group] = best_threshold

        return thresholds
```

---

## 6. Model Risk Management

### 6.1 Risk Assessment Framework

```python
class ModelRiskAssessment:
    """
    Assess and manage model risk.

    Risk Categories:
    - Data risk: Poor quality, bias, drift
    - Model risk: Poor performance, overfitting
    - Implementation risk: Bugs, integration issues
    - Operational risk: Downtime, security
    - Compliance risk: Regulatory violations
    - Reputational risk: PR issues, trust loss
    """

    def assess_model_risk(
        self,
        model_info: Dict,
        deployment_context: Dict
    ) -> Dict:
        """
        Comprehensive model risk assessment.

        Returns risk score and mitigation recommendations.
        """
        risk_assessment = {
            'overall_risk': 'low',  # low, medium, high, critical
            'risk_scores': {},
            'mitigations': []
        }

        # Data Risk
        data_risk = self._assess_data_risk(model_info)
        risk_assessment['risk_scores']['data'] = data_risk

        # Model Risk
        model_risk = self._assess_model_risk(model_info)
        risk_assessment['risk_scores']['model'] = model_risk

        # Operational Risk
        operational_risk = self._assess_operational_risk(deployment_context)
        risk_assessment['risk_scores']['operational'] = operational_risk

        # Compliance Risk
        compliance_risk = self._assess_compliance_risk(deployment_context)
        risk_assessment['risk_scores']['compliance'] = compliance_risk

        # Overall risk (max of individual risks)
        max_risk = max(risk_assessment['risk_scores'].values())
        risk_assessment['overall_risk'] = self._risk_level(max_risk)

        # Generate mitigations
        risk_assessment['mitigations'] = self._generate_mitigations(
            risk_assessment['risk_scores']
        )

        return risk_assessment

    def _assess_data_risk(self, model_info: Dict) -> float:
        """Assess data-related risks."""
        risk_score = 0

        # Check data quality
        if model_info.get('data_quality_score', 1.0) < 0.8:
            risk_score += 0.3

        # Check for bias
        if model_info.get('fairness_score', 1.0) < 0.8:
            risk_score += 0.4

        # Check data freshness
        days_since_training = (
            datetime.now() - model_info.get('training_date')
        ).days

        if days_since_training > 90:
            risk_score += 0.3

        return min(risk_score, 1.0)

    def _risk_level(self, score: float) -> str:
        """Convert risk score to level."""
        if score >= 0.7:
            return 'critical'
        elif score >= 0.5:
            return 'high'
        elif score >= 0.3:
            return 'medium'
        else:
            return 'low'
```

---

## 7. Regulatory Compliance

### 7.1 GDPR Right to Explanation

```python
class GDPRCompliance:
    """
    Ensure GDPR compliance for automated decision-making.

    Article 22: Right not to be subject to automated decision-making
    Article 13-15: Right to explanation
    """

    def provide_explanation(
        self,
        model,
        instance: np.ndarray,
        prediction: float,
        feature_names: List[str]
    ) -> Dict:
        """
        Provide GDPR-compliant explanation.

        Must include:
        - Logic involved in decision
        - Significance and consequences
        - How to challenge decision
        """
        explainer = SHAPExplainer(model, reference_data)

        explanation = explainer.explain_prediction(instance, feature_names)

        gdpr_explanation = {
            'decision': 'approve' if prediction >= 0.5 else 'deny',
            'logic': 'This decision was made by an automated system using machine learning.',
            'factors': explanation['feature_contributions'],
            'significance': 'This affects your ability to...',
            'consequences': 'If denied, you can...',
            'challenge_process': 'To challenge this decision, contact...',
            'human_review_available': True,
            'data_used': feature_names,
            'processing_timestamp': datetime.utcnow().isoformat()
        }

        return gdpr_explanation

    def enable_human_review(
        self,
        prediction: float,
        confidence: float,
        protected_attributes: Dict
    ) -> bool:
        """
        Determine if human review required.

        GDPR requires human oversight for high-impact decisions.
        """
        # Require human review if:
        # - Low confidence
        # - High impact decision
        # - Sensitive attributes involved

        if confidence < 0.7:
            return True

        if protected_attributes:
            return True

        return False
```

---

## 8. Governance Framework

### 8.1 Model Governance Board

```markdown
## Model Governance Board Structure

### Composition
- **ML Engineering Lead**: Technical oversight
- **Data Science Lead**: Model methodology
- **Product Manager**: Business alignment
- **Legal/Compliance**: Regulatory compliance
- **Ethics Officer**: Ethical considerations
- **Security Lead**: Security review

### Responsibilities
1. Approve models for production
2. Review model performance quarterly
3. Assess compliance with policies
4. Review incidents and near-misses
5. Update governance policies

### Meeting Cadence
- Monthly: Review new model approvals
- Quarterly: Production model review
- Ad-hoc: Incident response

### Decision Authority
- Production deployment: Requires majority approval
- High-risk models: Requires unanimous approval
- Policy updates: Requires 2/3 approval
```

### 8.2 Governance Policies

```python
class GovernancePolicies:
    """
    Enforce model governance policies.

    Policies cover:
    - Model approval process
    - Documentation requirements
    - Performance monitoring
    - Bias testing
    - Security requirements
    - Compliance checks
    """

    def check_policy_compliance(self, model_version: str) -> Dict:
        """
        Check if model complies with all governance policies.

        Returns compliance report.
        """
        compliance = {
            'compliant': True,
            'violations': [],
            'warnings': []
        }

        # Policy 1: Complete documentation
        if not self.has_complete_documentation(model_version):
            compliance['violations'].append("Incomplete documentation")
            compliance['compliant'] = False

        # Policy 2: Performance meets minimum threshold
        metrics = self.get_model_metrics(model_version)
        if metrics['accuracy'] < 0.75:
            compliance['violations'].append("Below minimum accuracy threshold")
            compliance['compliant'] = False

        # Policy 3: Bias assessment completed
        if not self.has_bias_assessment(model_version):
            compliance['violations'].append("Missing bias assessment")
            compliance['compliant'] = False

        # Policy 4: Security review passed
        if not self.passed_security_review(model_version):
            compliance['violations'].append("Security review not completed")
            compliance['compliant'] = False

        # Policy 5: Monitoring configured
        if not self.has_monitoring(model_version):
            compliance['warnings'].append("Monitoring not configured")

        return compliance
```

---

## Conclusion

**Key Takeaways:**

1. **Documentation**: Complete model cards for all production models
2. **Explainability**: Provide explanations for high-stakes decisions
3. **Fairness**: Test for bias across demographic groups
4. **Compliance**: Ensure regulatory requirements met
5. **Governance**: Establish approval processes and oversight

**Action Items:**

1. Create model cards for existing models
2. Implement SHAP explanations
3. Conduct fairness analysis
4. Establish governance board
5. Define and enforce policies
6. Regular compliance audits

**Remember**: Responsible AI is not optional - it's a business imperative.
