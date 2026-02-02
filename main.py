"""
Main Entry Point for Gold & Silver Prediction Agent System
"""
import sys
from datetime import datetime
from config import PREDICTION_HORIZONS, LEGAL_DISCLAIMER

from agents.ensemble_agent import EnsembleAgent
from reasoning.llm_reasoning import LLMReasoningLayer
from output.dashboard import Dashboard
from kpis import KPIEvaluator


def main():
    """Main execution function"""
    print("="*60)
    print("Gold & Silver Prediction Agent System")
    print("="*60)
    print(LEGAL_DISCLAIMER)
    print("\n")
    
    # Initialize components
    dashboard = Dashboard()
    reasoning_layer = LLMReasoningLayer()
    kpi_evaluator = KPIEvaluator()
    
    commodities = ["gold", "silver"]
    
    # Generate predictions for each commodity
    for commodity in commodities:
        print(f"\n{'='*60}")
        print(f"Analyzing {commodity.upper()}...")
        print(f"{'='*60}\n")
        
        # Create ensemble agent
        ensemble = EnsembleAgent(commodity=commodity)
        
        # Get predictions for different horizons
        predictions = {}
        for horizon_name, horizon_days in PREDICTION_HORIZONS.items():
            print(f"Generating {horizon_name} prediction ({horizon_days} days)...")
            
            try:
                prediction = ensemble.get_ensemble_prediction(horizon_days=horizon_days)
                predictions[horizon_name] = prediction
                
                # Generate explanation
                explanation = reasoning_layer.generate_explanation(prediction)
                
                # Update dashboard
                dashboard.update(commodity, prediction, explanation)
                
                # Record for KPI evaluation
                kpi_evaluator.record_prediction(prediction)
                
                print(f"  Signal: {prediction['signal'].upper()}")
                print(f"  Confidence: {prediction['confidence']:.1f}%")
                print(f"  Key Drivers: {', '.join(prediction['drivers'][:2])}")
                
            except Exception as e:
                print(f"  Error: {e}")
                continue
        
        # Generate and display report
        print(f"\n{'-'*60}")
        print(f"{commodity.upper()} REPORT")
        print(f"{'-'*60}")
        report = dashboard.generate_report(commodity)
        print(report)
    
    # Display summary
    print("\n" + "="*60)
    print("PREDICTION SUMMARY")
    print("="*60)
    summary = dashboard.get_summary()
    for commodity, data in summary.items():
        print(f"\n{commodity.upper()}:")
        print(f"  Signal: {data['signal'].upper()}")
        print(f"  Confidence: {data['confidence']:.1f}%")
        print(f"  Horizon: {data['horizon_days']} days")
    
    # Export dashboard data
    try:
        with open(f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            f.write(dashboard.to_json())
        print("\nDashboard data exported to JSON file.")
    except Exception as e:
        print(f"\nCould not export dashboard: {e}")
    
    print("\n" + "="*60)
    print("Analysis Complete")
    print("="*60)
    print(LEGAL_DISCLAIMER)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

