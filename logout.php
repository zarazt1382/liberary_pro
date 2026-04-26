<?php
session_start(); // شروع یا ادامه سشن

// پاک کردن تمام متغیرهای سشن
$_SESSION = array();

// اگر می‌خواهید سشن را کاملا از بین ببرید، کوکی سشن را هم پاک کنید.
// توجه: این کار باعث می‌شود که مرورگر سشن ID را هم پاک کند.
if (ini_get("session.use_cookies")) {
    $params = session_get_cookie_params();
    setcookie(session_name(), '', time() - 42000, $params["path"], $params["domain"],
        $params["secure"], $params["httponly"]
    );
}

// نابود کردن سشن
session_destroy();

// هدایت کاربر به صفحه لاگین
header("Location: login.php");
exit;
?>
