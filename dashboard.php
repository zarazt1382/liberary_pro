<?php
session_start();

// بررسی اینکه کاربر وارد شده است یا خیر
if (!isset($_SESSION['username'])) {
    header("Location: login.php");
    exit;
}

// مسیر فایل JSON - فرض می‌کنیم در همین پوشه است
$jsonFilePath = __DIR__ . '/library_data_fa.json';
$books_data = [];
$error_message = '';

// خواندن داده‌ها از فایل JSON
if (file_exists($jsonFilePath)) {
    $jsonString = file_get_contents($jsonFilePath);
    if ($jsonString === false) {
        $error_message = "خطا در خواندن فایل JSON.";
    } else {
        $decoded_data = json_decode($jsonString, true);
        if ($decoded_data === null && json_last_error() !== JSON_ERROR_NONE) {
            $error_message = "خطا در تجزیه فایل JSON: " . json_last_error_msg();
        } elseif (is_array($decoded_data)) {
            $books_data = $decoded_data;
        } else {
            $error_message = "محتوای فایل JSON معتبر نیست (باید آرایه باشد).";
            // اگر فایل خالی بود و json_decode null برگرداند، مشکلی نیست، فقط $books_data خالی می‌ماند.
            if ($jsonString === '' || $jsonString === '[]') {
                 $books_data = [];
            }
        }
    }
} else {
    // اگر فایل وجود نداشت، آن را ایجاد می‌کنیم (با محتوای آرایه خالی)
    if (file_put_contents($jsonFilePath, '[]') === false) {
        $error_message = "خطا در ایجاد فایل JSON.";
    } else {
        $books_data = []; // فایل جدید است و خالی خواهد بود
    }
}

// مرتب‌سازی کتاب‌ها بر اساس عنوان (اختیاری)
if (!empty($books_data) && is_array($books_data)) {
    usort($books_data, function($a, $b) {
        // اطمینان از وجود کلیدها قبل از مقایسه
        $titleA = isset($a['title_fa']) ? $a['title_fa'] : '';
        $titleB = isset($b['title_fa']) ? $b['title_fa'] : '';
        return strcasecmp($titleA, $titleB);
    });
}
?>
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل مدیریت کتاب</title>
    <style>
        body { font-family: 'Tahoma', sans-serif; margin: 0; padding: 0; background-color: #f4f7f6; direction: rtl; }
        .container { width: 95%; margin: 20px auto; background-color: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
        .welcome { color: #333; font-size: 1.1em; }
        .logout-link { color: #dc3545; text-decoration: none; font-weight: bold; }
        .logout-link:hover { text-decoration: underline; }
        h2 { color: #333; text-align: center; margin-bottom: 25px; }
        .actions { margin-bottom: 20px; text-align: center; }
        .add-button, .run-script-button {
            display: inline-block;
            padding: 10px 18px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.95em;
            margin: 5px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .add-button { background-color: #007bff; color: white; }
        .add-button:hover { background-color: #0056b3; }
        .run-script-button { background-color: #6c757d; color: white; }
        .run-script-button:hover { background-color: #5a6268; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: right; word-wrap: break-word; font-size: 0.9em; }
        th { background-color: #f8f9fa; color: #333; font-weight: bold; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        td a { color: #007bff; text-decoration: none; margin: 0 5px; }
        td a:hover { text-decoration: underline; }        
        .error-message { color: #dc3545; font-weight: bold; text-align: center; margin-bottom: 15px; }
        .no-books { text-align: center; color: #6c757d; padding: 20px; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div class="top-bar">
            <span class="welcome">سلام <?php echo htmlspecialchars($_SESSION['username']); ?> عزیز!</span>
            <a href="logout.php" class="logout-link">خروج</a>
        </div>

        <h2>لیست کتاب‌ها</h2>

        <?php if (!empty($error_message)): ?>
            <p class="error-message"><?php echo $error_message; ?></p>
        <?php endif; ?>

        <div class="actions">
            <a href="manage_book.php?action=add" class="add-button">امکانات</a>
            <!-- دکمه اجرای اسکریپت پایتون -->
            <button class="run-script-button" onclick="runUpdateScript()">اجرای اسکریپت به‌روزرسانی JSON</button>
        </div>

        <?php if (empty($error_message) && !empty($books_data) && is_array($books_data)): ?>
        <table>
            <thead>
                <tr>
                    <th>نام کتاب</th>
                    <th>نویسنده</th>
                    <th>مترجم</th>
                    <th>سال نشر</th>
                    <th>انتشارات</th>
                    <th>ویراست</th>
                    <th>نسخه</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($books_data as $book): ?>
                <tr>
                    <td><?php echo htmlspecialchars($book['book_name'] ?? '---'); ?></td>
                    <td><?php echo htmlspecialchars($book['author'] ?? '---'); ?></td>
                    <td><?php echo htmlspecialchars($book['translator'] ?? '---'); ?></td>
                    <td><?php echo htmlspecialchars($book['publish_year'] ?? '---'); ?></td>
                    <td><?php echo htmlspecialchars($book['publisher'] ?? '---'); ?></td>
                    <td><?php echo htmlspecialchars($book['edition'] ?? '---'); ?></td>
                    <td><?php echo htmlspecialchars($book['version'] ?? '---'); ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
        <?php elseif (empty($error_message) && (empty($books_data) || !is_array($books_data))): ?>
            <p class="no-books">هیچ کتابی یافت نشد. لطفا یک کتاب جدید اضافه کنید.</p>
        <?php endif; ?>
    </div>

    <script>
        function runUpdateScript() {
            if (confirm('آیا مطمئن هستید که می‌خواهید اسکریپت به‌روزرسانی فایل JSON را اجرا کنید؟')) {
                // اینجا فقط به فایل PHP هدایت می‌شویم که اسکریپت را اجرا می‌کند
                window.location.href = 'run_update_script.php';
            }
        }
    </script>
</body>
</html>
