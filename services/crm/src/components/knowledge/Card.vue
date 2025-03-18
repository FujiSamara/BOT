<script setup lang="ts">
const props = defineProps({
	list: {
		type: Array<String>,
	},
});
</script>
<template>
	<div>
		<ul>
			<li v-for="rec in props.list">
				{{ rec }}
			</li>
		</ul>
	</div>
</template>
<style scoped lang="scss"></style>
