function initializeTimer(duration) {
    let timer = duration;
    const timerElement = document.getElementById('timer');
    
    const countdown = setInterval(() => {
        const minutes = parseInt(timer / 60, 10);
        const seconds = parseInt(timer % 60, 10);
        
        timerElement.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        
        if (--timer < 0) {
            clearInterval(countdown);
            document.getElementById('quizForm').submit();
        }
    }, 1000);
}