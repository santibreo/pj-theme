var windowHeight = window.innerHeight;
var toc = document.querySelector('.toc');

// Factor of screen size that the element must cross
// before being considered visible
var TOP_MARGIN = 0.2,
    BOTTOM_MARGIN = 0.1;

window.onscroll = function () {syncview()};

function syncview() {
    tocItems = [].slice.call(toc.querySelectorAll('li'));

    // Cache element references and measurements
    tocItems = tocItems.map(function (item) {
        var anchor = item.querySelector('a');
        var target = document.getElementById(anchor.getAttribute('href').slice(1));

        return {
            listItem: item,
            anchor: anchor,
            target: target
        };
    });
    tocItems[0].listItem.classList.add('toc-title')

    // Remove missing targets
    tocItems = tocItems.filter(function (item) {
        return !!item.target;
    });

    tocItems.forEach(function (item) {
        var targetBounds = item.target.getBoundingClientRect();
        if (targetBounds.bottom > windowHeight * TOP_MARGIN && targetBounds.top < windowHeight * (1 - BOTTOM_MARGIN)) {
            //pathStart = Math.min( lastItem.pathStart, pathStart );
            item.listItem.classList.add('toc-visible');
        }
        else {
            item.listItem.classList.remove('toc-visible');
        }
    });
};

/*
    for (let i = 0; i <= tocItems.length - 1; i++) {
        console.log(i);
        let item = tocItems[i];
        var targetBounds = item.getBoundingClientRect();
        // Elements inside window
        if (targetBounds.bottom > windowHeight * TOP_MARGIN && targetBounds.top < windowHeight * (1 - BOTTOM_MARGIN)) {
            item.classList.add('toc-visible');
            console.log(targetBounds.bottom)
        }
        else {
            item.classList.remove('toc-visible');
        }
    };
*/
