<?php
// این فایل فقط به عنوان یک واسطه برای اجرای اسکریپت پایتون و هدایت کاربر عمل می‌کند.
// فرض بر این است که اسکریپت update_json.py در همان پوشه قرار دارد.

// فایل JSON که اسکریپت پایتون باید آن را بخواند و بروزرسانی کند.
$jsonFilePath = __DIR__ . '/library_data_fa.json';

// دستور اجرای اسکریپت پایتون
// **مهم**: مطمئن شوید که `python` در PATH سیستم شما موجود است.
// اگر اسکریپت پایتون نیاز به آرگومان دارد (مثلا مسیر فایل)، آن را اینجا اضافه کنید.
// در این مثال، فرض می‌کنیم اسکریپت پایتون خودش مسیر را می‌داند یا از یک روش دیگر استفاده می‌کند.
// اگر اسکریپت پایتون مسیر فایل JSON را به عنوان آرگومان می‌گیرد:
// $command = 'python update_json.py ' . escapeshellarg($jsonFilePath);
// اگر اسکریپت پایتون مسیر را در خود کد Hardcode کرده یا خودش پیدا می‌کند:
$command = 'python update_json.py';


$output = '';
$error = '';
$return_var = null; // متغیر برای نگهداری کد بازگشتی

// اجرای دستور در shell
// exec برای اجرای دستور و گرفتن خروجی آن استفاده می‌شود.
// ممکن است نیاز باشد دسترسی exec را در تنظیمات php.ini فعال کنید.
// اگر exec کار نکرد، راه دیگر استفاده از shell_exec یا passthru است.
// برای امنیت بیشتر، از escapeshellcmd استفاده شده است.
@exec($command . ' 2>&1', $output_lines, $return_var); // 2>&1 برای گرفتن خطاها و خروجی‌ها با هم
$output = implode("\n", $output_lines);

$message = $_GET['message'] ?? 'عملیات به‌روزرسانی فایل JSON با موفقیت انجام شد.'; // پیام پیش‌فرض

if ($return_var !== 0) {
    // اگر اسکریپت با خطا اجرا شد
    $message = "خطا در اجرای اسکریپت پایتون: " . (!empty($output) ? $output : 'خطای ناشناخته.');
    // ممکن است بخواهید پیام خطا را به کاربر نشان دهید یا در لاگ ثبت کنید
    // echo "<pre>Error executing command: " . htmlspecialchars($command) . "</pre>";
    // echo "<pre>Output:\n" . htmlspecialchars($output) . "</pre>";
}

// اضافه کردن پیام از URL (اگر وجود داشت) به پیام نهایی
$url_message = $_GET['message'] ?? '';
if (!empty($url_message) && $return_var === 0) {
    $message = urldecode($url_message); // استفاده از پیام ارسال شده از PHP
} elseif ($return_var !== 0) {
     // اگر خطای اسکریپت بود، همان پیام خطا را نشان بده
     $message = "خطا هنگام اجرای اسکریپت پایتون: " . (!empty($output) ? htmlspecialchars($output) : 'خطای ناشناخته.');
}


// هدایت کاربر به داشبورد با پیام (چه موفقیت چه خطا)
header("Location: dashboard.php?message=" . urlencode($message));
exit;

?>
