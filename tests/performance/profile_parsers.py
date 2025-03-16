import cProfile
import pstats
import os
import psutil
import time
from typing import Dict, List
from src.parsers.parser_factory import DocumentParserFactory

class ParserProfiler:
    def __init__(self):
        self.factory = DocumentParserFactory()
        self.profiler = cProfile.Profile()
        self.results: Dict[str, Dict] = {}
        
    def profile_parser(self, file_path: str) -> Dict:
        """Profile a single parser's performance."""
        file_type = os.path.splitext(file_path)[1][1:]
        parser = self.factory.create_parser(file_path)
        
        # Memory usage before parsing
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # Start profiling
        start_time = time.time()
        self.profiler.enable()
        
        # Parse document
        result = parser.parse(file_path)
        
        # Stop profiling
        self.profiler.disable()
        end_time = time.time()
        
        # Memory usage after parsing
        memory_after = process.memory_info().rss
        memory_used = memory_after - memory_before
        
        # Get profiling statistics
        stats = pstats.Stats(self.profiler)
        
        return {
            'file_type': file_type,
            'processing_time': end_time - start_time,
            'memory_used': memory_used,
            'total_functions': len(stats.stats),
            'cumulative_time': sum(stat[3] for stat in stats.stats.values()),
            'function_calls': sum(stat[0] for stat in stats.stats.values())
        }
    
    def profile_batch(self, files: List[str]) -> None:
        """Profile multiple files and collect statistics."""
        for file_path in files:
            result = self.profile_parser(file_path)
            self.results[file_path] = result
    
    def generate_report(self) -> str:
        """Generate a performance report."""
        report = ["Performance Profiling Report", "=" * 30, ""]
        
        for file_path, stats in self.results.items():
            report.extend([
                f"File: {os.path.basename(file_path)}",
                f"Type: {stats['file_type']}",
                f"Processing Time: {stats['processing_time']:.2f} seconds",
                f"Memory Used: {stats['memory_used'] / 1024 / 1024:.2f} MB",
                f"Total Functions: {stats['total_functions']}",
                f"Total Function Calls: {stats['function_calls']}",
                f"Cumulative Time: {stats['cumulative_time']:.2f} seconds",
                "-" * 30,
                ""
            ])
        
        return "\n".join(report)

def main():
    # Test files
    test_files = [
        '../test_data/sample_resume.pdf',
        '../test_data/sample_resume.docx',
        '../test_data/sample_resume.txt'
    ]
    
    # Create profiler
    profiler = ParserProfiler()
    
    # Profile parsers
    profiler.profile_batch(test_files)
    
    # Generate and save report
    report = profiler.generate_report()
    
    with open('performance_report.txt', 'w') as f:
        f.write(report)
    
    print("Performance report generated successfully!")

if __name__ == '__main__':
    main() 