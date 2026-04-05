/**
 * Этот скрипт должен быть вставлен в Google Apps Script.
 * Он принимает данные от Telegram-бота и отправляет HTML-письмо через Gmail.
 */

function doPost(e) {
  try {
    // Получаем данные, которые прислал наш Python-бот
    var data = JSON.parse(e.postData.contents);
    var email = data.email;
    var body = data.body;

    // Отправляем письмо через твой аккаунт Google
    MailApp.sendEmail({
      to: email,
      subject: "Playerok • Уведомление о заказе",
      htmlBody: body
    });

    // Возвращаем боту ответ, что всё прошло успешно
    return ContentService.createTextOutput("Success");
    
  } catch (error) {
    // Если что-то пошло не так, возвращаем текст ошибки
    return ContentService.createTextOutput("Error: " + error.toString());
  }
}
