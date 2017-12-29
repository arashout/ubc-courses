/**
 * Calculate a 32 bit FNV-1a hash
 * Found here: https://gist.github.com/vaiorabbit/5657561
 * Ref.: http://isthe.com/chongo/tech/comp/fnv/
 *
 * @param {string} message the input value
 * @param {boolean} [asString=false] set to true to return the hash value as 
 *     8-digit hex string instead of an integer
 * @param {integer} [seed] optionally pass the hash of the previous chunk
 * @returns {integer | string}
 */
export function hashFnv32a(message: string, asString = true, seed = 0x811c9dc5) {
    let i;
    let l;
    let hval = seed;

    for (i = 0, l = message.length; i < l; i++) {
        hval ^= message.charCodeAt(i);
        hval += (hval << 1) + (hval << 4) + (hval << 7) + (hval << 8) + (hval << 24);
    }
    if( asString ){
        // Convert to 8 digit hex string
        return ("0000000" + (hval >>> 0).toString(16)).substr(-8);
    }
    return hval >>> 0;
}

function digestTest(){
    const courses = ['MATH100', 'MATH101'];
    console.log(hashFnv32a(courses.join()));
}