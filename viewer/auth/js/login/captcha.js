
async function initCaptcha() {
    $('#captchaImage').click(async function() {
        $('#captchaImage').attr('src', 'http://127.0.0.1:5000/generate_code?' + Date.now());
    });

    $('#submitBtn').click(verifyCaptcha);
}

async function verifyCaptcha() {
    var code = $('#captchaInput').val().trim();

    try {
        var response = await $.ajax({
            url: 'http://127.0.0.1:5000/verify_code',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ code: code })
        });

        if (response.valid) {
            $('#captchaImage').hide();
        // location.reload();
        } else {
            alert('Invalid captcha. Please try again.');
        }
    } catch (error) {
        alert('An error occurred. Please try again later.');
    }
}