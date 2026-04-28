<?php
// اتصال به پایگاه داده
$connection = new mysqli("localhost", "root", "", "library_db");
$connection->set_charset("utf8mb4");

if ($connection->connect_error) {
    die("خطا در اتصال به پایگاه داده: " . $connection->connect_error);
}

// خواندن اطلاعات از جدول کتاب‌ها
$result = $connection->query("SELECT * FROM books ORDER BY id DESC");
?>

<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>کتابخانه شخصی</title>
    <style>
        body {
            font-family: 'Tahoma', 'Segoe UI', sans-serif;
            background-color: #f4f7fa;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 28px;
        }
        #searchInput {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            padding: 14px 20px;
            font-size: 17px;
            border: 2px solid #bdc3c7;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            box-sizing: border-box;
            display: block;
            transition: border-color 0.3s;
        }
        #searchInput:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.15);
        }
        table {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            border-collapse: collapse;
            background-color: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        }
        th {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 16px;
            font-size: 16px;
            text-align: center;
        }
        td {
            padding: 14px;
            text-align: right;
            border-bottom: 1px solid #ecf0f1;
        }
        tr {
            transition: background-color 0.3s;
        }
        tr:hover {
            background-color: #ebf3fd;
        }
        tr:nth-child(even) {
            background-color: #f8fbff;
        }
        tr:nth-child(even):hover {
            background-color: #e3f2fd;
        }
        @media screen and (max-width: 768px) {
            body {
                padding: 10px;
            }
            h1 {
                font-size: 24px;
            }
            table {
                font-size: 14px;
            }
            th, td {
                padding: 10px;
            }
            #searchInput {
                font-size: 16px;
                padding: 12px 16px;
            }
        }
        @media screen and (max-width: 480px) {
            table {
                display: block;
                overflow-x: auto;
                white-space: nowrap;
            }
        }
    </style>
</head>

<body>
<h1>کتابخانه شخصی</h1>

<input type="text" id="searchInput" onkeyup="searchTable()" 
       placeholder="جستجو در نام کتاب، نویسنده، مترجم، انتشارات و ...">

<table id="bookTable" border="1" cellpadding="8">
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
    <?php while($row = $result->fetch_assoc()): ?>
        <tr>
            <td><?= htmlspecialchars($row['book_name']) ?></td>
            <td><?= htmlspecialchars($row['author']) ?></td>
            <td><?= htmlspecialchars($row['translator']) ?></td>
            <td><?= htmlspecialchars($row['publish_year']) ?></td>
            <td><?= htmlspecialchars($row['publisher']) ?></td>
            <td><?= htmlspecialchars($row['edition']) ?></td>
            <td><?= htmlspecialchars($row['version']) ?></td>
        </tr>
    <?php endwhile; ?>
    </tbody>
</table>

<script>
function searchTable() {
    const input = document.getElementById("searchInput");
    const filter = input.value.toUpperCase();
    const table = document.getElementById("bookTable");
    const tr = table.getElementsByTagName("tr");

    for (let i = 1; i < tr.length; i++) {
        const td = tr[i].getElementsByTagName("td");
        let visible = false;
        for (let j = 0; j < td.length; j++) {
            if (td[j]) {
                const txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    visible = true;
                    break;
                }
            }
        }
        tr[i].style.display = visible ? "" : "none";
    }
}
</script>

</body>
</html>

<?php $connection->close(); ?>
