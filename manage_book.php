<?php
session_start();

// Database connection details
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "library_db";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Function to update library_data_fa.json
function updateJsonFile($conn) {
    $sql = "SELECT id, book_name, author,translator, publish_year,publisher,edition,version FROM books";
    $result = $conn->query($sql);
    $books = array();
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $books[] = $row;
        }
    }
    // Use JSON_UNESCAPED_UNICODE for proper Persian characters
    if (file_put_contents('library_data_fa.json', json_encode($books, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT))) {
        // Optionally, log success or return a success message
        // echo "JSON file updated successfully.";
    } else {
        // Optionally, log error or return an error message
        // echo "Error updating JSON file.";
    }
}


// Handle different actions: add, edit, delete
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['action'])) {
        $action = $_POST['action'];

        if ($action == 'add' || $action == 'edit') {
            $id = isset($_POST['id']) ? intval($_POST['id']) :0; 
            $book_name = $conn->real_escape_string($_POST['book_name']);
            $author = $conn->real_escape_string($_POST['author']);
            $translator = $conn->real_escape_string($_POST['translator']);
            $publish_year = intval($_POST['publish_year']);
            $publisher = $conn->real_escape_string($_POST['publisher']);
            $edition = $conn->real_escape_string($_POST['edition']);
            $version =intval($_POST['version']);

            // If adding, we need to get the next available ID
            if ($action == 'add') {
                // Find the maximum current ID and add 1
                $sql_get_max_id = "SELECT MAX(id) AS max_id FROM books";
                $result_max_id = $conn->query($sql_get_max_id);
                $row_max_id = $result_max_id->fetch_assoc();
                $id = ($row_max_id['max_id'] === null) ? 1 : $row_max_id['max_id'] + 1;

                $sql = "INSERT INTO books (id, book_name, author,translator, publish_year,publisher,edition,version) VALUES ('$id', '$book_name', '$author','$translator', '$publish_year','$publisher','$edition', '$version')";
            } else { // Editing existing book
                $sql = "UPDATE books SET book_name='$book_name', author='$author',translator='$translator', publish_year='$publish_year',publisher='$publisher',edition='$edition', version='$version' WHERE id='$id'";
            }

            if ($conn->query($sql) === TRUE) {
                $_SESSION['message'] = ($action == 'add') ? "کتاب با موفقیت اضافه شد." : "کتاب با موفقیت ویرایش شد.";
                // Update the JSON file after successful database operation
                updateJsonFile($conn);
            } else {
                $_SESSION['message'] = "خطا در ذخیره کتاب: " . $conn->error;
            }

        } elseif ($action == 'delete') {
            $id = intval($_POST['id']);
            $sql = "DELETE FROM books WHERE id='$id'";

            if ($conn->query($sql) === TRUE) {
                $_SESSION['message'] = "کتاب با موفقیت حذف شد.";
                // Update the JSON file after successful database operation
                updateJsonFile($conn);
            } else {
                $_SESSION['message'] = "خطا در حذف کتاب: " . $conn->error;
            }
        }
    }
    // Redirect back to the manage_book.php page to show messages and updated list
    header("Location: manage_book.php");
    exit();
}

// Fetch books for display
$books = array();
$sql = "SELECT id, book_name, author,translator, publish_year,publisher,edition,version FROM books ORDER BY id ASC";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $books[] = $row;
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت کتابخانه</title>
    <style>
        body { font-family: 'Tahoma', sans-serif; background-color: #f4f7f6; color: #333; margin: 20px; }
        .container { max-width: 1500px; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #2c3e50; text-align: center; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { padding: 12px 15px; text-align: right; border: 1px solid #ddd; }
        th { background-color: #34495e; color: white; }
        tr:nth-child(even) { background-color: #ecf0f1; }
        .action-buttons button, .action-buttons a {
            background-color: #3498db; color: white; padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; margin-left: 5px; text-decoration: none; font-size: 14px;
        }
        .form-section { background-color: #ecf0f1; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .form-section label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-section input[type="text"], .form-section input[type="number"] {
            width: calc(100% - 20px); padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px;
        }
        .form-section button {
            background-color: #2ecc71; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px;
        }
        .form-section button:hover { opacity: 0.9; }
        .message { padding: 10px; margin-bottom: 15px; border-radius: 4px; text-align: center; font-weight: bold; }
        .message.success { background-color: #2ecc71; color: white; }
        .message.error { background-color: #e74c3c; color: white; }
        .hidden { display: none; }
        .btn-edit, .btn-delete { padding: 10px 12px; border-radius: 10px; font-size: 0.85em; margin-left: 10px; }
        .btn-edit { background-color: #ffc107; color: #333; border: none; cursor: pointer; }
        .btn-delete { background-color: #dc3545; color: white; border: none; cursor: pointer; }
        .form-section button {display: block; margin: 15px auto; }
        .book-list-section { margin-top: 30px; padding: 20px; background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .book-list-section h2 {text-align: center;color: #333; margin-bottom: 20px;}
        .book-list-section table { width: 100%; border-collapse: collapse;}
        .book-list-section th,.book-list-section td { border: 1px solid #ccc; padding: 10px;text-align: center;}
        .book-list-section th { background-color: #007bff; color: white;}
        .book-list-section tr:nth-child(even) {background-color: #f2f2f2;}
        .book-list-section button { padding: 6px 12px;border: none;border-radius: 10px;cursor: pointer;color: white; margin-bottom: 10px;}

    </style>
</head>
<body>
    <div class="container">
        <?php
        // Display session message if it exists
        if (isset($_SESSION['message'])) {
            echo '<div class="message ' . (strpos($_SESSION['message'], 'موفقیت') !== false ? 'success' : 'error') . '">' . $_SESSION['message'] . '</div>';
            unset($_SESSION['message']); // Clear the message after displaying
        }
        ?>

        <!-- Add/Edit Form -->
        <div class="form-section">
            <h2>افزودن یا ویرایش کتاب</h2>
            <form id="book-form" method="POST" action="manage_book.php">
                <input type="hidden" name="action" id="action" value="add">
                <input type="hidden" name="id" id="book_id" value="">

                <label for="book_name">عنوان کتاب:</label>
                <input type="text" id="book_name" name="book_name" required>

                <label for="author">نویسنده:</label>
                <input type="text" id="author" name="author" required>

                <label for="translator">مترجم:</label>
                <input type="text" id="translator" name="translator" >            

                <label for="publish_year">سال انتشار:</label>
                <input type="number" id="publish_year" name="publish_year" >

                <label for="publisher">انتشارات :</label>
                <input type="text" id="publisher" name="publisher" >

                <label for="edition">ویراست :</label>
                <input type="text" id="edition" name="edition" >

                <label for="version">نسخه:</label>
                <input type="text" id="version" name="version">

                <button  type="submit" id="form-button">افزودن کتاب</button>
            </form>
        </div>

        <!-- Book List -->
        <div class="book-list-section">
            <h2>لیست کتاب‌ها</h2>
            <?php if (!empty($books)): ?>
                <table>
                    <thead>
                        <tr>
                            <th>ردیف</th>
                            <th>نام کتاب</th>
                            <th>نویسنده</th>
                            <th>مترجم</th>
                            <th>سال نشر</th>
                            <th>انتشارات</th>
                            <th>ویراست</th>
                            <th>نسخه</th>
                            <th>عملیات</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($books as $book): ?>
                            <tr>
                                <td><?php echo htmlspecialchars($book['id'] ?? '---'); ?></td>
                                <td><?php echo htmlspecialchars($book['book_name'] ?? '---'); ?></td>
                                <td><?php echo htmlspecialchars($book['author'] ?? '---'); ?></td>
                                <td><?php echo htmlspecialchars($book['translator'] ?? '---'); ?></td>
                                <td><?php echo htmlspecialchars($book['publish_year'] ?? '---'); ?></td>
                                <td><?php echo htmlspecialchars($book['publisher'] ?? '---'); ?></td>
                                <td><?php echo htmlspecialchars($book['edition'] ?? '---'); ?></td>
                                <td><?php echo htmlspecialchars($book['version'] ?? '---'); ?></td>
                                <td>
                                    <button class="btn-edit" onclick="editBook(<?php echo htmlspecialchars(json_encode($book)); ?>)">ویرایش</button>
                                    <form method="POST" action="manage_book.php" style="display:inline-block;">
                                        <input type="hidden" name="action" value="delete">
                                        <input type="hidden" name="id" value="<?php echo htmlspecialchars($book['id']); ?>">
                                        <button class="btn-delete" type="submit" class="delete" onclick="return confirm('آیا از حذف این کتاب مطمئن هستید؟');">حذف</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            <?php else: ?>
                <p style="text-align: center;">هیچ کتابی در کتابخانه ثبت نشده است.</p>
            <?php endif; ?>
        </div>
    </div>

    <script>
        function editBook(bookData) {
            // Populate the form with book data
            document.getElementById('book_id').value = bookData.id;
            document.getElementById('book_name').value = bookData.book_name;
            document.getElementById('author').value = bookData.author;
            document.getElementById('translator').value = bookData.translator;
            document.getElementById('publish_year').value = bookData.publish_year;
            document.getElementById('publisher').value = bookData.publisher;
            document.getElementById('edition').value = bookData.edition;
            document.getElementById('version').value = bookData.version;

            // Change form action to 'edit' and update button text
            document.getElementById('action').value = 'edit';
            document.getElementById('form-button').innerText = 'ویرایش کتاب';
            document.getElementById('book-form').scrollIntoView({ behavior: 'smooth' });
        }

    </script>
</body>
</html>
