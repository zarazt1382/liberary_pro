<?php
session_start(); // شروع یا ادامه سشن

// اطلاعات کاربری تعریف شده (در دنیای واقعی این اطلاعات باید از دیتابیس یا فایل کانفیگ امن خوانده شوند)
$valid_username = "admin"; // نام کاربری دلخواه شما
$valid_password = "1234"; // رمز عبور دلخواه شما (باید هش شود!)

// دریافت اطلاعات از فرم لاگین
$username = $_POST['username'] ?? ''; // استفاده از عملگر Null Coalescing برای جلوگیری از خطا
$password = $_POST['password'] ?? '';

// بررسی صحت اطلاعات
if ($username === $valid_username && $password === $valid_password) {
    // اطلاعات صحیح است، کاربر لاگین شد
    $_SESSION['loggedin'] = true;
    $_SESSION['username'] = $username;

    // هدایت کاربر به صفحه داشبورد
    header("Location: dashboard.php");
    exit; // پایان اسکریپت بعد از هدایت
} else {
    // اطلاعات اشتباه است، بازگشت به صفحه لاگین با پیام خطا
    header("Location: login.php?error=1");
    exit; // پایان اسکریپت بعد از هدایت
}
?>
