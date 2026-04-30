class RecommendationService:
    def __init__(self, recommender, sanitizer):
        self._recommender = recommender
        self._sanitize = sanitizer

    def build_library_sample(self, books):
        sample = []
        for book in books:
            sample.append({
                'title': self._sanitize(book.title),
                'author': self._sanitize(book.author),
                'category': book.category,
                'available_count': book.available_count,
                'isbn': book.isbn
            })
        return sample

    def get_suggestions(self, survey_data, books, top_n=5):
        library_sample = self.build_library_sample(books)
        return self._recommender(survey_data, library_sample, top_n=top_n)
