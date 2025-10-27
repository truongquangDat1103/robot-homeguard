import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Create admin user
  const hashedPassword = await bcrypt.hash('admin123', 10);
  const admin = await prisma.user.upsert({
    where: { email: 'admin@homeguard.com' },
    update: {},
    create: {
      email: 'admin@homeguard.com',
      password: hashedPassword,
      name: 'Admin User',
      role: 'ADMIN',
    },
  });
  console.log('✓ Created admin user:', admin.email);

  // Create test user
  const testHashedPassword = await bcrypt.hash('test123', 10);
  const testUser = await prisma.user.upsert({
    where: { email: 'user@homeguard.com' },
    update: {},
    create: {
      email: 'user@homeguard.com',
      password: testHashedPassword,
      name: 'Test User',
      role: 'USER',
    },
  });
  console.log('✓ Created test user:', testUser.email);

  // Create default settings
  await prisma.settings.upsert({
    where: { key: 'system.initialized' },
    update: {},
    create: {
      key: 'system.initialized',
      value: { initialized: true, timestamp: new Date() },
    },
  });

  await prisma.settings.upsert({
    where: { key: 'sensor.update_interval' },
    update: {},
    create: {
      key: 'sensor.update_interval',
      value: { interval: 1000 }, // 1 second
    },
  });

  await prisma.settings.upsert({
    where: { key: 'robot.battery_warning' },
    update: {},
    create: {
      key: 'robot.battery_warning',
      value: { threshold: 20 }, // 20%
    },
  });

  console.log('✓ Created default settings');
  console.log('🎉 Seeding completed!');
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });