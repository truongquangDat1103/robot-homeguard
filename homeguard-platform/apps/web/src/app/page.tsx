/**
 * Home Page - Landing page của website
 */

import Link from 'next/link';

export default function HomePage() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800">
            <div className="max-w-4xl px-4 text-center">
                {/* Logo */}
                <div className="mb-8">
                    <h1 className="text-6xl font-bold text-blue-600 dark:text-blue-400">
                        🏠 HomeGuard
                    </h1>
                    <p className="mt-4 text-xl text-gray-600 dark:text-gray-300">
                        Smart Home Robot Monitoring & Control Platform
                    </p>
                </div>

                {/* Features */}
                <div className="mb-12 grid gap-8 md:grid-cols-3">
                    <div className="rounded-lg border bg-white p-6 shadow-sm dark:bg-gray-800">
                        <div className="mb-4 text-4xl">📊</div>
                        <h3 className="mb-2 text-lg font-semibold">Real-time Monitoring</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Theo dõi cảm biến và robot real-time với WebSocket
                        </p>
                    </div>

                    <div className="rounded-lg border bg-white p-6 shadow-sm dark:bg-gray-800">
                        <div className="mb-4 text-4xl">🤖</div>
                        <h3 className="mb-2 text-lg font-semibold">Robot Control</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Điều khiển robot từ xa qua giao diện web
                        </p>
                    </div>

                    <div className="rounded-lg border bg-white p-6 shadow-sm dark:bg-gray-800">
                        <div className="mb-4 text-4xl">🎯</div>
                        <h3 className="mb-2 text-lg font-semibold">AI Recognition</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Nhận diện khuôn mặt và phát hiện chuyển động
                        </p>
                    </div>
                </div>

                {/* CTA Buttons */}
                <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
                    <Link
                        href="/dashboard"
                        className="rounded-lg bg-blue-600 px-8 py-3 text-white font-semibold hover:bg-blue-700 transition-colors"
                    >
                        Go to Dashboard
                    </Link>
                    <Link
                        href="/login"
                        className="rounded-lg border border-gray-300 px-8 py-3 font-semibold hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-800 transition-colors"
                    >
                        Login
                    </Link>
                </div>

                {/* Footer */}
                <div className="mt-16 text-sm text-gray-500">
                    <p>Built with Next.js, React, TypeScript, and WebSocket</p>
                </div>
            </div>
        </div>
    );
}