window.queryParams = new URLSearchParams(window.location.search);

const COMPONENTS  = {
    submitContainer: {
        elt: document.getElementById('submitContainer'),
        h1: document.querySelector('#submitContainer h1'),
        pre: document.querySelectorAll('#submitContainer pre')[0],
        pre2: document.querySelectorAll('#submitContainer pre')[1],
        error: document.querySelector('#submitContainer .error'),
        tryAgainLink: document.querySelector('#submitContainer a'),
    },

    setTimeContainer: {
        elt: document.getElementById('setTimeContainer'),
        h1: document.querySelector('#setTimeContainer h1'),
        select: document.querySelector('#setTimeContainer select'),
        addTime: document.querySelector('#setTimeContainer a.addTime'),
        saveButton: document.querySelector('#setTimeContainer button'),
    },
}

if (queryParams.has('lang')) {
    const lang = window.LANGS[queryParams.get('lang')];
    window.LANG = lang;
    window.LANG_CODE = queryParams.get('lang');

    COMPONENTS.submitContainer.h1.textContent = lang.submit.sending;
    COMPONENTS.submitContainer.error.textContent = lang.submit.error;
    COMPONENTS.submitContainer.tryAgainLink.textContent = lang.submit.tryAgain;

    COMPONENTS.setTimeContainer.h1.textContent = lang.setTime.selectTime;
    COMPONENTS.setTimeContainer.saveButton.textContent = lang.setTime.save;
} else {
    throw new Error("lang parameter is not passed");
}

function hideEverything() {
    hide(COMPONENTS.submitContainer.elt);
    hide(COMPONENTS.setTimeContainer.elt);
}

function show(elt) {
    elt.classList.remove("displayNone");
}

function hide(elt) {
    elt.classList.add("displayNone");
}

class DataSubmitComponent {
    constructor(app) {
        this.app = app;
        this.queryId = app.initDataUnsafe.query_id;
        this.data = null;
    }

    _showData(data) {
        hideEverything();

        show(COMPONENTS.submitContainer.elt);
        show(COMPONENTS.submitContainer.pre);

        hide(COMPONENTS.submitContainer.error);
        hide(COMPONENTS.submitContainer.tryAgainLink);
        hide(COMPONENTS.submitContainer.pre2);

        COMPONENTS.submitContainer.pre.textContent = data;
    }

    _showError(error) {
        show(COMPONENTS.submitContainer.error);
        show(COMPONENTS.submitContainer.tryAgainLink);
        show(COMPONENTS.submitContainer.pre2);
        COMPONENTS.submitContainer.pre2.textContent = error;

        const tryAgainHandler = (e) => {
            e.preventDefault();
            hide(COMPONENTS.submitContainer.error);
            hide(COMPONENTS.submitContainer.tryAgainLink);
            hide(COMPONENTS.submitContainer.pre2);
            this.submitData(this.dataProvider);
            COMPONENTS.submitContainer.tryAgainLink.removeEventListener("click", tryAgainHandler);
        }

        COMPONENTS.submitContainer.tryAgainLink.addEventListener('click', tryAgainHandler);
    }

    async submitData(dataProvider) {
        const urlParams = new URLSearchParams(window.location.search);
        const env = urlParams.get('env') || "prod";

        this.dataProvider = dataProvider;
        const data = this.dataProvider();
        this._showData(data);
        const url = `https://boo.great-site.net/quotes.php?env=${env}&lang_code=${window.LANG_CODE}&query_id=` + encodeURIComponent(this.queryId) + '&data=' + encodeURIComponent(data)+'&_=' + new Date().getTime();
        const corsUrl = url; //'https://corsproxy.io/?' + encodeURIComponent(url);

        if (!AbortSignal.timeout) {
            AbortSignal.timeout = function timeout(ms) {
                const ctrl = new AbortController()
                setTimeout(() => ctrl.abort(), ms)
                return ctrl.signal
            }
        }

        try {
            const response = await fetch(corsUrl, {mode: 'cors', signal: AbortSignal.timeout(15000)});
            if (!response.ok) {
                this._showError(window.LANG.errBackend + `: ${response.status} ${response.statusText}`);
                return;
            }
            const json = await response.json();
            if (json.status < 200 || json.status > 299) {
                this._showError(window.LANG.errTelegram + `: ${json.status} ${json.response}`);
                return;
            }
            this.app.close();
        } catch (err) {
            this._showError(err.message);
        }

    }
}

class TimeManager {
    constructor() {
        const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        const offsetSecs = -(new Date().getTimezoneOffset()) * 60;
        console.log(timeZone, offsetSecs);

        const template = COMPONENTS.setTimeContainer.select.parentElement;
        const root = template.parentElement;
        template.remove();

        let isFirst = true;
        const mins = (window.queryParams.get("mins") || ("" + (9*60))).split(",");
        const isMinsUtc = window.queryParams.has("is_mins_utc");

        function syncFirstSelectorVisibility() {
            const aList = root.querySelectorAll('a');
            if (aList.length === 1) {
                aList[0].style.visibility = 'hidden';
            } else {
                aList[1].style.visibility = 'visible';
            }
        }

        for (let min of mins) {
            min = parseInt(min);
            if (isMinsUtc) {
                min += Math.floor(offsetSecs / 60);
                min = (Math.floor(min / 30) * 30) % (24 * 60);
            }
            const clone = template.cloneNode(true);
            const select = clone.querySelector('select');
            select.value = min;
            if (isFirst) {
                clone.querySelector('a').style.visibility = 'hidden';
            }
            clone.querySelector('a').addEventListener('click', (e) => {
                e.preventDefault();
                clone.remove();
                syncFirstSelectorVisibility();
            });
            root.appendChild(clone);
            isFirst = false;
        }

        COMPONENTS.setTimeContainer.addTime.addEventListener('click', (e) => {
            e.preventDefault();
            const clone = template.cloneNode(true);
            clone.querySelector('a').addEventListener('click', (e) => {
                e.preventDefault();
                clone.remove();
                syncFirstSelectorVisibility();
            });
            root.appendChild(clone);
            syncFirstSelectorVisibility();
        });

        COMPONENTS.setTimeContainer.saveButton.addEventListener('click', (e) => {
            e.preventDefault();
            const times = Array.from(root.querySelectorAll('select'))
                .map((select) => select.value).join(',');
            const data = JSON.stringify({times, timeZone, offsetSecs});
            new DataSubmitComponent(window?.Telegram?.WebApp).submitData(() => data);
        });
        syncFirstSelectorVisibility();
    }
}

// new DataSubmitComponent(window?.Telegram?.WebApp).submitData(() => 'hi');

new TimeManager();