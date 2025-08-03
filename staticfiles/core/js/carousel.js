let currentSlide = 0;
const slides = document.getElementById("carouselSlides");
function showSlide(index) {
     const total = slides.children.length;
    currentSlide = (index + total) % total;
     slides.style.transform = `translateX(-${currentSlide * 100}%)`;
        }

        function nextSlide() {
        showSlide(currentSlide + 1);
        }

        function prevSlide() {
        showSlide(currentSlide - 1);
        }

        setInterval(nextSlide, 5000);