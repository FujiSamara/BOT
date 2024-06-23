<template>
    <div class="cross-wrapper">
        <div class="c"></div>
        <div class="c"></div>
    </div>
</template>
<script>
export default {
    name: "window-cross"
}
</script>
<style>
    .cross-wrapper {
        width: 24px;
        height: 24px;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    .c {
        position: absolute;
        width: 2px;
        height: 100%;
        background-color: #993CA6;
    }
    .c:nth-child(1) {
        transform: rotate(45deg)
    }
    .c:nth-child(2) {
        transform: rotate(-45deg)
    }
</style>