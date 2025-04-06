const eventSource = new EventSource("/sse");

eventSource.onmessage = function(event) {
    sendNotification('Новый снимок', {
        body: 'Вас снимает скрытая камера',
        dir: 'auto'
    });
};

eventSource.onerror = function(error) {
    console.error('Ошибка при подключении к SSE:', error);
};

function sendNotification(title, options) {
    if (!("Notification" in window)) {
        alert('Ваш браузер не поддерживает HTML Notifications, его необходимо обновить.');
    }

    else if (Notification.permission === "granted") {
        var notification = new Notification(title, options);
        function clickFunc() { alert('Пасхалка'); }
        notification.onclick = clickFunc;
    }

    else {
        Notification.requestPermission(function (permission) {
        if (permission === "granted") {
            var notification = new Notification(title, options);
        } else {
            alert('Вы запретили показывать уведомления'); 
        }
        });
    }
}