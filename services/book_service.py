from library_app.models import Book


class BookService:
    def get_available_books_grouped(self):
        books = Book.query.filter(Book.available_count > 0).all()
        return self._group_books(books)

    def get_all_books_grouped(self):
        books = Book.query.all()
        return self._group_books(books)

    def get_book(self, book_id):
        return Book.query.get(book_id)

    def get_library_sample(self, limit=20):
        return Book.query.limit(limit).all()

    def match_suggestions(self, suggestions):
        matched = []
        for suggestion in suggestions:
            title = (suggestion.get('title') or '').strip()
            author = (suggestion.get('author') or '').strip()
            reason = suggestion.get('reason', '')
            confidence = suggestion.get('confidence', 0)

            book = Book.query.filter(
                Book.title.ilike(f"%{title}%"),
                Book.author.ilike(f"%{author}%")
            ).first()

            matched.append({
                'suggested_title': title,
                'suggested_author': author,
                'reason': reason,
                'confidence': confidence,
                'in_library': bool(book),
                'book_id': book.id if book else None,
                'available_count': book.available_count if book else 0
            })

        return matched

    def _group_books(self, books):
        books_by_category = {}
        for book in books:
            books_by_category.setdefault(book.category, []).append(book)

        sorted_books = dict(sorted(books_by_category.items()))
        for category in sorted_books:
            sorted_books[category] = sorted(sorted_books[category], key=lambda b: b.title)

        return sorted_books
