import os
import json
import time
from datetime import datetime
from process_reports import process_single_report

def process_batch_reports(folder_path="all", max_reports=5):

    # Get list of files
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found")
        return
    
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    total_files = len(files)
    
    if max_reports:
        files = files[:max_reports]
    
    print(f"Processing {len(files)} reports from {total_files} total files...")
    print("="*60)
    
    results = []
    
    for i, filename in enumerate(files):
        print(f"Processing {i+1}/{len(files)}: {filename}")
        
        try:
            start_time = time.time()

            # Read the report
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # Process through AI
            result = process_single_report(report_content)
            
            # Add metadata
            result['filename'] = filename
            result['processing_time'] = time.time() - start_time
            
            results.append(result)
            
            print(f"Completed in {time.time() - start_time:.1f}s\n")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            continue
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"results/batch_results_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nBatch processing complete!")
    print(f"Results saved to: {output_file}")
    print(f"Successfully processed: {len(results)} reports")

if __name__ == "__main__":
    # Test with 5 reports first
    process_batch_reports(max_reports=5)