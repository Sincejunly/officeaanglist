self.onmessage = async (e) => {
    const { formData, total } = e.data;
    let currentChunk = 0;

    while (currentChunk < total) {
        try {
            const response = await fetch('http://127.0.0.1:5000/upload', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                currentChunk++;
                self.postMessage({ success: true, current: currentChunk, total });
            } else {
                self.postMessage({ success: false });
            }
        } catch (error) {
            self.postMessage({ success: false });
        }
    }
};
