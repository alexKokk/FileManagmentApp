const deleteButton = document.querySelectorAll('.delete-file-btn');

deleteButton.forEach((button) => {
  button.addEventListener('click', async (event) => {
    const fileId = event.target.dataset.fileId;

    try {
      const response = await fetch('/delete-file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fileId }),
      });

      const data = await response.json();

      if (response.ok) {
        // File deleted successfully
        console.log(data.message);
        // Update UI to remove the deleted file (e.g., remove the list item)
        const fileListItem = event.target.parentElement;
        fileListItem.parentNode.removeChild(fileListItem);
      } else {
        // Handle error cases based on status code
        console.error(data.message);
        // Display an error message to the user (e.g., using alert or toast)
        alert(data.message);
      }
    } catch (error) {
      console.error('Error deleting file:', error);
      // Display a generic error message to the user
      alert('An error occurred while deleting the file.');
    }
  });
});
