function searchBooks() {
    const searchQuery = document.getElementById('searchBar').value.trim();
    const filterBy = document.getElementById('sortOptions').value;
    const genreFilter = document.getElementById('genreOptions').value; 
    const booksContainer = document.querySelector('.books-container');

    
    if (searchQuery.length === 0 && genreFilter.length === 0) {
        window.location.href = '/explore_library';
        return;
    }

    let searchURL = `/search?query=${encodeURIComponent(searchQuery)}&filter_by=${filterBy}`;
    if (genreFilter) {
        searchURL += `&genre=${encodeURIComponent(genreFilter)}`; 
    }

    fetch(searchURL)
        .then(response => response.json())
        .then(data => {
            
            booksContainer.innerHTML = '';

            if (data.length === 0) {
                
                booksContainer.innerHTML = '<div class="not-found">Not Found</div>';
                return;
            }

            
            data.forEach(book => {
                const bookCard = document.createElement('div');
                bookCard.className = 'book-card';
                bookCard.innerHTML = `
                    <img src="/static/images/${book.image_filename}" alt="${book.title}">
                    <div class="book-info">
                        <h3>${book.title}</h3>
                        <p>by ${book.author}</p>
                        <p>Genre: ${book.genre}</p>
                        <p>Published: ${book.publish_date}</p>
                        <p>ISBN: ${book.isbn}</p>
                    </div>
                `;
                booksContainer.appendChild(bookCard);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            
        });
}
document.querySelectorAll('.book-card').forEach(card => {
    card.onclick = () => showDetails(card);
});

function showDetails(book) {
    
    document.getElementById('bookModal').style.display = 'block';
    document.getElementById('modalBookImage').src = book.querySelector('img').src;
    document.getElementById('modalBookTitle').textContent = book.querySelector('.book-title').textContent;
    document.getElementById('modalBookAuthor').textContent = book.querySelector('.book-author').textContent;
    document.getElementById('modalBookGenre').textContent = book.querySelector('.Genre').textContent;
    document.getElementById('modalBookPublished').textContent = book.querySelector('.PublishDate').textContent;
    document.getElementById('modalBookIsbn').textContent = book.querySelector('.isbn').textContent;
    document.getElementById('modalBookDescription').textContent = book.querySelector('.description').textContent;
    document.getElementById('modalBookPages').textContent = book.querySelector('.page_count').textContent;
    document.getElementById('modalBookLanguage').textContent = book.querySelector('.language').textContent;
    
    

    
    document.getElementById('bookModal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('bookModal').style.display = 'none';
}
$('.close').click(function() {
    $(this.parentElement).fadeOut('slow');
});
