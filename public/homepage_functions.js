function toggleLike(index) {
    if (posts[index].liked) {
        posts[index].likes--;
    } else {
        posts[index].likes++;
    }
    posts[index].liked = !posts[index].liked;
    renderPosts();
}

document.getElementById('createPostBtn').addEventListener('click', function() {
    document.getElementById('popup').style.display = 'block';
});

document.getElementById('cancelPostBtn').addEventListener('click', function() {
    document.getElementById('popup').style.display = 'none';
});

document.getElementById('submitPostBtn').addEventListener('click', function() {
    const content = document.getElementById('postContent').value.trim();
    if (content !== '') {
        const post = {
            username: 'User', // You can replace 'User' with actual username
            content: content,
            likes: 0,
            liked: false
        };
        posts.push(post);
        renderPosts();
        document.getElementById('popup').style.display = 'none';
        document.getElementById('postContent').value = '';
    }
});