  // src/utils/fileValidation.js
  export const validateImageFile = (file) => {
    if (!file) return 'No file selected.';
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(file.type)) return 'Please upload a valid image (JPEG, PNG, GIF).';
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) return 'File size exceeds 5MB limit.';
    return null;
  };