function changeUserAvatar(userId) {
    var intranetUrl = 'https://intranet.stxnext.pl:443/api/images/users/' + userId;
    jQuery('.avatar').html(jQuery('<img src="' + intranetUrl + '" alt="' + intranetUrl + '" />'));
}
