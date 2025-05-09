
document.addEventListener('DOMContentLoaded', function() {
    // Enable the enhanced search if available
    const extraSearchData = document.querySelector('script[src$="extra-search-data.json"]');
    if (extraSearchData) {
        // Load and process the enhanced search data
        fetch(extraSearchData.getAttribute('src'))
            .then(response => response.json())
            .then(data => {
                window.docstraExtraSearchData = data;
                console.log('Enhanced search data loaded');
            })
            .catch(err => console.error('Error loading enhanced search data:', err));
    }
    
    // Add syntax highlighting enhancements
    document.querySelectorAll('pre code').forEach(block => {
        // Add line numbers if not already present
        if (!block.classList.contains('linenos')) {
            const lineNumbers = block.innerHTML.split('\n').length;
            if (lineNumbers > 3) {
                block.classList.add('line-numbers');
            }
        }
    });
});
