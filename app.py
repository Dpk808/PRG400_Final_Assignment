import os

from werkzeug.security import generate_password_hash

from library_app import create_app
from library_app.extensions import db
from library_app.models import Book, User


app = create_app()


def init_db():
    with app.app_context():
        db.create_all()

        if User.query.first() is None:
            admin = User(
                username="admin",
                password=generate_password_hash("admin123"),
                role="admin",
            )

            student1 = User(
                username="student1",
                password=generate_password_hash("pass123"),
                role="student",
            )
            student2 = User(
                username="student2",
                password=generate_password_hash("pass123"),
                role="student",
            )

            db.session.add_all([admin, student1, student2])
            db.session.commit()

            books = []
            isbn_counter = 1000000000

            novels = [
                ("The Great Gatsby", "F. Scott Fitzgerald"), ("To Kill a Mockingbird", "Harper Lee"),
                ("1984", "George Orwell"), ("Pride and Prejudice", "Jane Austen"),
                ("The Catcher in the Rye", "J.D. Salinger"), ("Jane Eyre", "Charlotte Brontë"),
                ("Wuthering Heights", "Emily Brontë"), ("The Adventures of Huckleberry Finn", "Mark Twain"),
                ("Moby Dick", "Herman Melville"), ("War and Peace", "Leo Tolstoy"),
                ("The Hobbit", "J.R.R. Tolkien"), ("The Lord of the Rings", "J.R.R. Tolkien"),
                ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling"), ("The Hunger Games", "Suzanne Collins"),
                ("Twilight", "Stephenie Meyer"), ("The Chronicles of Narnia", "C.S. Lewis"),
                ("Alice in Wonderland", "Lewis Carroll"), ("The Picture of Dorian Gray", "Oscar Wilde"),
                ("Frankenstein", "Mary Shelley"), ("Dracula", "Bram Stoker"),
                ("The Strange Case of Dr Jekyll and Mr Hyde", "Robert Louis Stevenson"), ("The Time Machine", "H.G. Wells"),
                ("Twenty Thousand Leagues Under the Sea", "Jules Verne"), ("Around the World in 80 Days", "Jules Verne"),
                ("A Tale of Two Cities", "Charles Dickens"), ("Great Expectations", "Charles Dickens"),
                ("Oliver Twist", "Charles Dickens"), ("David Copperfield", "Charles Dickens"),
                ("The Odyssey", "Homer"), ("The Iliad", "Homer"), ("Hamlet", "William Shakespeare"),
                ("Romeo and Juliet", "William Shakespeare"), ("Macbeth", "William Shakespeare"),
                ("A Midsummer Night's Dream", "William Shakespeare"), ("The Tempest", "William Shakespeare"),
                ("Les Misérables", "Victor Hugo"), ("The Hunchback of Notre-Dame", "Victor Hugo"),
                ("The Count of Monte Cristo", "Alexandre Dumas"), ("The Three Musketeers", "Alexandre Dumas"),
                ("The Man in the Iron Mask", "Alexandre Dumas"), ("Crime and Punishment", "Fyodor Dostoevsky"),
                ("The Brothers Karamazov", "Fyodor Dostoevsky"), ("Anna Karenina", "Leo Tolstoy"),
                ("Vanity Fair", "William Thackeray"), ("The Tenant of Wildfell Hall", "Anne Brontë"),
                ("The Mayor of Casterbridge", "Thomas Hardy"), ("Tess of the d'Urbervilles", "Thomas Hardy"),
                ("Jude the Obscure", "Thomas Hardy"), ("Middlemarch", "George Eliot"),
                ("Silas Marner", "George Eliot"), ("Jane Austen Novels", "Jane Austen"),
                ("North and South", "Elizabeth Gaskell"), ("The Woman in White", "Wilkie Collins"),
                ("The Moonstone", "Wilkie Collins"), ("Rebecca", "Daphne du Maurier"),
                ("Jamaica Inn", "Daphne du Maurier"), ("Beloved", "Toni Morrison"),
                ("The Bluest Eye", "Toni Morrison"), ("Song of Solomon", "Toni Morrison"),
                ("One Hundred Years of Solitude", "Gabriel García Márquez"), ("Love in the Time of Cholera", "Gabriel García Márquez"),
                ("The Unbearable Lightness of Being", "Milan Kundera"), ("Invisible Man", "Ralph Ellison"),
                ("The Grapes of Wrath", "John Steinbeck"), ("East of Eden", "John Steinbeck"),
                ("Of Mice and Men", "John Steinbeck"), ("Catch-22", "Joseph Heller"),
                ("Slaughterhouse-Five", "Kurt Vonnegut"), ("Fahrenheit 451", "Ray Bradbury"),
                ("The Martian", "Andy Weir"), ("The Midnight Library", "Matt Haig"),
                ("Educated", "Tara Westover"), ("The Book Thief", "Markus Zusak"),
                ("All the Light We Cannot See", "Anthony Doerr"), ("The Nightingale", "Kristin Hannah"),
                ("Before We Were Yours", "Lisa Wingate"), ("The Alice Network", "Kate Quinn"),
                ("The Shadow of the Wind", "Carlos Ruiz Zafón"), ("Mrs. Dalloway", "Virginia Woolf"),
                ("Ulysses", "James Joyce"), ("In Search of Lost Time", "Marcel Proust"),
            ]
            for i, (title, author) in enumerate(novels[:100]):
                books.append(
                    Book(
                        title=title,
                        author=author,
                        isbn=f"979-{isbn_counter + i}",
                        category="Novels",
                        available_count=2,
                    )
                )

            self_help = [
                ("Atomic Habits", "James Clear"), ("The Habit Loop", "Charles Duhigg"),
                ("Thinking, Fast and Slow", "Daniel Kahneman"), ("The Power of Now", "Eckhart Tolle"),
                ("How to Win Friends and Influence People", "Dale Carnegie"), ("The 7 Habits of Highly Effective People", "Stephen R. Covey"),
                ("Mindset", "Carol S. Dweck"), ("Emotional Intelligence", "Daniel Goleman"),
                ("The 4-Hour Workweek", "Tim Ferriss"), ("Deep Work", "Cal Newport"),
                ("Outliers", "Malcolm Gladwell"), ("Blink", "Malcolm Gladwell"),
                ("The Tipping Point", "Malcolm Gladwell"), ("Grit", "Angela Duckworth"),
                ("The Growth Mindset", "Carol Dweck"), ("Sapiens", "Yuval Noah Harari"),
                ("Homo Deus", "Yuval Noah Harari"), ("21 Lessons for the 21st Century", "Yuval Noah Harari"),
                ("Educated", "Tara Westover"), ("The Year of Yes", "Shonda Rhimes"),
                ("Becoming", "Michelle Obama"), ("A Promised Land", "Barack Obama"),
                ("The Courage to Be Disliked", "Ichiro Kishimi"), ("Steal Like an Artist", "Austin Kleon"),
                ("Show Your Work", "Austin Kleon"), ("The Art of Asking", "Amanda Palmer"),
                ("Essentialism", "Greg McKeown"), ("The One Thing", "Gary W. Keller"),
                ("The Power of Focus", "Jack Canfield"), ("The Magic of Thinking Big", "David Schwartz"),
                ("You Are a Badass", "Jen Sincero"), ("The Subtle Art of Not Giving a F*ck", "Mark Manson"),
                ("Can't Hurt Me", "David Goggins"), ("Extreme Ownership", "Jocko Willink"),
                ("The Obstacle Is the Way", "Ryan Holiday"), ("Ego Is the Enemy", "Ryan Holiday"),
                ("Stillness Is the Key", "Ryan Holiday"), ("I Will Teach You to Be Rich", "Ramit Sethi"),
                ("Your Money or Your Life", "Vicki Robin"), ("Money: Master the Game", "Tony Robbins"),
                ("Awaken the Giant Within", "Tony Robbins"), ("The Art of Negotiation", "Marc Cramer"),
                ("Never Split the Difference", "Chris Voss"), ("Crucial Conversations", "Kerry Patterson"),
                ("Difficult Conversations", "Douglas Stone"), ("Getting to Yes", "Roger Fisher"),
                ("The 5 Love Languages", "Gary Chapman"), ("Men Are from Mars Women Are from Venus", "John Gray"),
                ("Attached", "Amir Levine"), ("Why We Love", "Helen Fisher"),
                ("Essentialism: The Disciplined Pursuit", "Greg McKeown"), ("The Gifts of Imperfection", "Brené Brown"),
                ("Dare to Lead", "Brené Brown"), ("Rising Strong", "Brené Brown"),
                ("The Body Keeps the Score", "Bessel van der Kolk"), ("What Happened to You", "Bruce D. Perry"),
                ("How to Do Nothing", "Jenny Odell"), ("The Loneliness Epidemic", "Vivek Murthy"),
                ("Lost Connections", "Johann Hari"), ("The Midnight Library", "Matt Haig"),
                ("Think and Grow Rich", "Napoleon Hill"), ("The Science of Self-Discipline", "Peter Hollins"),
                ("A Man's Search for Meaning", "Viktor Frankl"), ("The Purpose Driven Life", "Rick Warren"),
                ("Man's Search for Meaning", "Viktor Frankl"), ("The Road Less Traveled", "M. Scott Peck"),
                ("Feeling Good", "David D. Burns"), ("The Anxiety and Phobia Workbook", "Edmund J. Bourne"),
                ("Mind Over Mood", "Dennis Greenberger"), ("Emotional Freedom", "Judith Orloff"),
                ("The Untethered Soul", "Michael A. Singer"), ("The Inner Game of Tennis", "W. Timothy Gallwey"),
                ("Zen and the Art of Motorcycle Maintenance", "Robert M. Pirsig"), ("The Monk Who Sold His Ferrari", "Robin Sharma"),
                ("Rework", "Jason Fried"), ("Zero to One", "Peter Thiel"), ("Lean Startup", "Eric Ries"),
            ]
            for i, (title, author) in enumerate(self_help[:100]):
                books.append(
                    Book(
                        title=title,
                        author=author,
                        isbn=f"979-{isbn_counter + 100 + i}",
                        category="Self-Help",
                        available_count=2,
                    )
                )

            biographies = [
                ("Steve Jobs", "Walter Isaacson"), ("Leonardo da Vinci", "Walter Isaacson"),
                ("Elon Musk", "Walter Isaacson"), ("Albert Einstein", "Walter Isaacson"),
                ("Benjamin Franklin", "Walter Isaacson"), ("A Brief History of Time", "Stephen Hawking"),
                ("The Universe in a Nutshell", "Stephen Hawking"), ("I.M. Pei: A Life", "Gao Zhanxiang"),
                ("Churchill: A Life", "Martin Gilbert"), ("Napoleon: A Life", "Andrew Roberts"),
                ("Cleopatra: A Life", "Stacy Schiff"), ("Alexander Hamilton", "Ron Chernow"),
                ("Washington: A Life", "Ron Chernow"), ("Grant", "Ron Chernow"),
                ("Outliers", "Malcolm Gladwell"), ("When Genius Failed", "Roger Lowenstein"),
                ("The Innovators", "Walter Isaacson"), ("Marie Curie: A Life", "Susan Quinn"),
                ("Darwin: Portrait of a Genius", "Paul Barrett"), ("Oppenheimer: His Life and Times", "Irving Lewis"),
                ("The Wright Brothers", "David McCullough"), ("1776", "David McCullough"),
                ("Truman", "David McCullough"), ("John Adams", "David McCullough"),
                ("Thomas Jefferson", "Jon Meacham"), ("Lincoln", "David Donald"),
                ("FDR: The Years That Changed America", "Harlow Giles Unger"), ("The Real Lincoln", "Thomas J. DiLorenzo"),
                ("A People's History of the United States", "Howard Zinn"), ("Founding Mothers", "Cokie Roberts"),
            ]
            for i, (title, author) in enumerate(biographies):
                books.append(
                    Book(
                        title=title,
                        author=author,
                        isbn=f"979-{isbn_counter + 200 + i}",
                        category="Biographies",
                        available_count=2,
                    )
                )

            coding = [
                ("Python Crash Course", "Eric Matthes"), ("Clean Code", "Robert C. Martin"),
                ("The Pragmatic Programmer", "Andrew Hunt"), ("Code Complete", "Steve McConnell"),
                ("Refactoring", "Martin Fowler"), ("Design Patterns", "Gang of Four"),
                ("The Mythical Man-Month", "Frederick Brooks"), ("Introduction to Algorithms", "Cormen"),
                ("The C Programming Language", "Kernighan & Ritchie"), ("JavaScript: The Good Parts", "Douglas Crockford"),
                ("You Don't Know JS", "Kyle Simpson"), ("Eloquent JavaScript", "Marijn Haverbeke"),
                ("Learning Python", "Mark Lutz"), ("Fluent Python", "Luciano Ramalho"),
                ("Java: The Complete Reference", "Herbert Schildt"), ("Effective Java", "Joshua Bloch"),
                ("Java Concurrency in Practice", "Brian Goetz"), ("Mastering Regular Expressions", "Jeffrey Friedl"),
                ("SQL Performance Explained", "Markus Winand"), ("MongoDB: The Definitive Guide", "Shannon Bradshaw"),
                ("PostgreSQL: Up and Running", "Regina Obe"), ("MySQL 8.0 Reference Manual", "MySQL Documentation"),
                ("HTML & CSS", "Jon Duckett"), ("Responsive Web Design", "Ethan Marcotte"),
                ("The Principles of Object-Oriented Design", "Robert C. Martin"), ("Software Architecture Patterns", "Mark Richards"),
                ("Building Microservices", "Sam Newman"), ("Site Reliability Engineering", "Niall Richard Murphy"),
                ("DevOps Handbook", "Gene Kim"), ("The Phoenix Project", "Gene Kim"),
                ("Docker in Action", "Jeff Nickoloff"), ("Kubernetes in Action", "Marko Lukša"),
                ("Terraform in Action", "Scott Winkler"), ("Infrastructure as Code", "Kief Morris"),
                ("Continuous Delivery", "Jez Humble"), ("Accelerate", "Nicole Forsgren"),
                ("The Five Orders of Ignorance", "Andy Hunt"), ("Software Craftsmanship", "Sandro Mancuso"),
                ("97 Things Every Programmer Should Know", "Kevlin Henney"), ("A Practical Guide to Computer Architecture", "Daniel Kleidman"),
                ("Computer Organization and Design", "Patterson & Hennessy"), ("Digital Design and Computer Architecture", "Harris & Harris"),
                ("Operating Systems Design and Implementation", "Andrew Tanenbaum"), ("Modern Operating Systems", "Andrew Tanenbaum"),
                ("Computer Networks", "Andrew Tanenbaum"), ("Networks", "Kurose & Ross"),
                ("Web Security Testing Cookbook", "Stuttard & Pinto"), ("Web Application Security", "Andrew Hoffman"),
                ("The Art of Software Security Testing", "Art of Software Security Testing"), ("Hacking: The Art of Exploitation", "Jon Erickson"),
                ("Malware Analysis", "Michael Sikorski"), ("The Web Application Hacker's Handbook", "Stuttard & Pinto"),
                ("Machine Learning in Action", "Peter Harrington"), ("Hands-On Machine Learning", "Aurélien Géron"),
                ("Introduction to Statistical Learning", "James et al"), ("Deep Learning", "Goodfellow, Bengio & Courville"),
                ("Natural Language Processing with Python", "Bird, Klein & Loper"), ("Computer Vision", "Richard Szeliski"),
                ("Programming Collective Intelligence", "Toby Segaran"), ("Data Mining", "Han, Kamber & Pei"),
                ("Cryptography and Network Security", "William Stallings"), ("Applied Cryptography", "Bruce Schneier"),
                ("Agile Software Development", "Robert C. Martin"), ("Scrum and XP from the Trenches", "Henrik Kniberg"),
                ("User Stories Applied", "Mike Cohn"), ("Test Driven Development", "Kent Beck"),
                ("The Cucumber Book", "Matt Wynne"), ("BDD in Action", "John Ferguson Smart"),
                ("RESTful Web Services", "Leonard Richardson"), ("Designing Web APIs", "Brenda Jin"),
                ("API Design Best Practices", "Various Authors"), ("GraphQL in Action", "Samer Buna"),
            ]
            for i, (title, author) in enumerate(coding[:100]):
                books.append(
                    Book(
                        title=title,
                        author=author,
                        isbn=f"979-{isbn_counter + 300 + i}",
                        category="Programming",
                        available_count=2,
                    )
                )

            others = [
                ("A Brief History of Time", "Stephen Hawking"), ("The Universe in a Nutshell", "Stephen Hawking"),
                ("Cosmos", "Carl Sagan"), ("The Grand Design", "Stephen Hawking"),
                ("The Selfish Gene", "Richard Dawkins"), ("The Blind Watchmaker", "Richard Dawkins"),
                ("The God Delusion", "Richard Dawkins"), ("The Fabric of the Cosmos", "Brian Greene"),
                ("The Elegant Universe", "Brian Greene"), ("Something Deeply Hidden", "Sean Carroll"),
                ("The Order of Time", "Carlo Rovelli"), ("Seven Brief Lessons on Physics", "Carlo Rovelli"),
                ("A Realm Enchanted", "Susan Schlee"), ("The Periodic Table", "Primo Levi"),
                ("The Story of Philosophy", "Will Durant"), ("Critique of Pure Reason", "Immanuel Kant"),
                ("Meditations", "Marcus Aurelius"), ("The Republic", "Plato"),
                ("The Ethics", "Aristotle"), ("Being and Nothingness", "Jean-Paul Sartre"),
                ("Existentialism is a Humanism", "Jean-Paul Sartre"), ("The Philosophy of the Present", "George Herbert Mead"),
                ("Phenomenology of Spirit", "G.W.F. Hegel"), ("Capital", "Karl Marx"),
                ("The Communist Manifesto", "Karl Marx"), ("The Prince", "Niccolò Machiavelli"),
                ("Leviathan", "Thomas Hobbes"), ("The Social Contract", "Jean-Jacques Rousseau"),
                ("A Theory of Justice", "John Rawls"), ("Anarchy, State, and Utopia", "Robert Nozick"),
                ("The Second Sex", "Simone de Beauvoir"), ("The Master and Margarita", "Mikhail Bulgakov"),
                ("Crime and Punishment", "Fyodor Dostoevsky"), ("Notes from Underground", "Dostoevsky"),
                ("The Brothers Karamazov", "Dostoevsky"), ("The Idiot", "Dostoevsky"),
                ("Blood Meridian", "Cormac McCarthy"), ("No Country for Old Men", "Cormac McCarthy"),
            ]
            for i, (title, author) in enumerate(others):
                books.append(
                    Book(
                        title=title,
                        author=author,
                        isbn=f"979-{isbn_counter + 400 + i}",
                        category="Others",
                        available_count=2,
                    )
                )

            db.session.add_all(books)
            db.session.commit()

            print(f"Database initialized with {len(books)} books!")


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
