$(document).ready(function() {
    var currentIndex = 0;
    var images = $(".hotel-photo");
    var totalImages = images.length;

    function showImage(index) {
        images.hide();
        $(images[index]).show();
    }

    function updateNavigationButtons(index) {
        if (index === 0) {
            $(".prev").hide();
            $(".next").show();
        } else if (index === totalImages - 1) {
            $(".prev").show();
            $(".next").hide();
        } else {
            $(".prev").show();
            $(".next").show();
        }
    }

    $(".prev").click(function() {
        currentIndex = Math.max(0, currentIndex - 1);
        showImage(currentIndex);
        updateNavigationButtons(currentIndex);
    });

    $(".next").click(function() {
        currentIndex = Math.min(totalImages - 1, currentIndex + 1);
        showImage(currentIndex);
        updateNavigationButtons(currentIndex);
    });

    // Показать первое изображение при загрузке страницы
    showImage(currentIndex);
    updateNavigationButtons(currentIndex);
});

